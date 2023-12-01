import calendar
from django.shortcuts import get_object_or_404, render, redirect
from decimal import Decimal
from orders.models import Order, OrderItem
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Category 
from acount.models import  Wallet,Wallet_History
from django.contrib import messages
from django.http import HttpResponse
from .forms import AdminReturnResponseForm
from .models import Coupon,Banner
from django.db.models import Count, Q, Sum
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear
from .forms import CouponForm
from .forms import EditCouponForm
from .forms import ReturnReasonForm
from orders.models import Order, ReturnRequest
from django.db.models import Count, Avg
from django.db.models.functions import ExtractMonth
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO



# Create your views here.
@never_cache
def admin_dsh(request):
    if request.user.is_authenticated:
        return render(request, "admin/admin_dsh.html")
    else:
        return redirect("home")

# def dashboard(request):
#     order_list = Order.objects.filter(status="delivered")
#     orders = Order.objects.annotate(month=ExtractMonth("updated")).values("month").annotate(count=Count("id")).values("month","count")
#     month_list = []
#     total_orders = []

#     for o in orders:
#         month_list.append(calendar.month_name[o["month"]])
#         total_orders.append(o["count"])
#     context = {
#         "orders" : orders,
#         "month" : month_list,
#         "total_orders" : total_orders,
#     }
#     return render(request,'admin/dashboard.html',context)

# @login_required
# @staff_member_required
def dashboard(request):
    active_users = User.objects.filter(is_active=True).exclude(is_superuser=True)
    total_active_users_count = active_users.count()
    products = Product.objects.filter(best_sellers__gt=0).order_by('-best_sellers')
    # Monthly sales data
    orders_month_report = (
        Order.objects.annotate(month=ExtractMonth("created"))
        .values("month")
        .annotate(monthly_orders_count=Count("id"))
        .annotate(monthly_sales=Sum("total_paid"))
        .values("month", "monthly_orders_count", "monthly_sales")
    )
    month = []
    total_orders_per_month = []
    total_sales_per_month = []

    for order in orders_month_report:
        month.append(calendar.month_name[order["month"]])
        total_orders_per_month.append(order["monthly_orders_count"])
        total_sales_per_month.append(order["monthly_sales"])

    # Daily sales data
    current_month = timezone.now().month
    current_year = timezone.now().year
    orders_daily_report = (
        Order.objects.filter(billing_status='bank')  # Adjust the status filter as needed
        .filter(created__month=current_month, created__year=current_year)
        .annotate(day=ExtractDay("created"))
        .values("day")
        .annotate(daily_orders_count=Count("id"))
        .annotate(daily_sales=Sum("total_paid"))
        .values("day", "daily_orders_count", "daily_sales")
)

    day = []
    total_orders_per_day = []
    total_sales_per_day = []

    for order in orders_daily_report:
        day.append(order["day"])
        total_orders_per_day.append(order["daily_orders_count"])
        total_sales_per_day.append(order["daily_sales"])

    # Yearly sales count
    orders_year_report = (
        Order.objects.annotate(year=ExtractYear("created"))
        .values("year")
        .annotate(yearly_orders_count=Count("id"))
        .annotate(yearly_sales=Sum("total_paid"))
        .values("year", "yearly_orders_count", "yearly_sales")
    )
    year = []
    total_orders_per_year = []
    total_sales_per_year = []

    for order in orders_year_report:
        year.append(order["year"])
        total_orders_per_year.append(order["yearly_orders_count"])
        total_sales_per_year.append(order["yearly_sales"])

    orders = Order.objects.filter(Q(status='delivered')|Q(billing_status='bank'))
    balance = Order.objects.filter(status='delivered').aggregate(
        total_sales=Sum("total_paid")
    )
    
    
    product_data = []
    for product in products:
        total_quantity_sold = OrderItem.objects.filter(product=product).aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_income = total_quantity_sold * product.price
        product_data.append({
            'product': product,
            'total_quantity_sold': total_quantity_sold,
            'total_income': total_income,
        })
        
    
    total_income = Order.objects.filter(Q(billing_status='bank')|Q(status='delivered')).aggregate(total_income=Sum('total_paid'))['total_income'] or 0
    total_orders_count = Order.objects.count()
    order_items = Order.objects.aggregate(order_sum=Sum("total_paid"))
    context = {
        'product_data': product_data,
        "total_active_users_count": total_active_users_count,
        "total_orders_count": total_orders_count,
        "total_income": total_income,
        "orders": orders,
        "balance": balance,
        "sales": order_items,
        "month": month,
        "total_orders_per_month": total_orders_per_month,
        "total_sales_per_month": total_sales_per_month,
        "day": day,
        "total_orders_per_day": total_orders_per_day,
        "total_sales_per_day": total_sales_per_day,
        "year": year,
        "total_orders_per_year": total_orders_per_year,
        "total_sales_per_year": total_sales_per_year,
    }
    return render(request,'admin/dashboard.html',context)


def generate_pdf(request):
    # Create a PDF file
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # Your table data
    orders = Order.objects.all()

    # Set up the PDF table headers
    headers = ["Customer", "CONTACT", "DATE", "ADDRESS", "Total Paid"]
    col_widths = [pdf.stringWidth(header, "Helvetica", 10) for header in headers]
    table_width = sum(col_widths)
    table_start_x = (letter[0] - table_width) / 2
    y_position = 750

    # Write headers to PDF
    for i, header in enumerate(headers):
        pdf.drawString(table_start_x + sum(col_widths[:i]), y_position, header)

    # Write data to PDF
    for order in orders:
        y_position -= 20
        pdf.drawString(table_start_x, y_position, order.full_name)
        pdf.drawString(table_start_x + col_widths[0], y_position, order.phone)
        pdf.drawString(table_start_x + col_widths[0] + col_widths[1], y_position, str(order.created))
        pdf.drawString(table_start_x + col_widths[0] + col_widths[1] + col_widths[2], y_position, order.address1)
        pdf.drawString(table_start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3], y_position, str(order.total_paid))

    pdf.save()

    # File response with the PDF content
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="orders.pdf"'
    return response



def banner(request):
    banners= Banner.objects.all()
    return render(request,'admin/show_banner.html',{'banners':banners})

def add_banner(request):
    if request.user.is_authenticated:
        return render(request, "admin/add_banner.html")
    else:
        return redirect("home")
    
def add_banner_action(request):
    if request.method == "POST":
        new_banner = request.POST.get("new_banner")
        link = request.POST.get("link")
        img = request.FILES.get("img")
        existing_category = Category.objects.filter(title=new_banner)

        if existing_category.exists():
            messages.error(request, "Category already exists")
            return redirect("add_banner")
        else:
            banner = Banner(title=new_banner, image=img,link=link)
            banner.save()

    return redirect("banner")


def banner_action(request,bid):
    banner = Banner.objects.get(id=bid)
    if banner.is_active:
        banner.is_active = False
    else:
        banner.is_active = True
    banner.save()
    return redirect("banner")

    
def edit_banner(request,bid):
    if request.user.is_authenticated:
        banners = Banner.objects.get(id=bid)
        return render(request, "admin/edit_banner.html", {'banners': banners})
    else:
        return redirect("home")



def edt_banner_action(request):
    if request.method == "POST":
        banner_id = request.POST.get("id")
        new_banner_name = request.POST.get("newcategory")  # Corrected variable name
        new_banner_img = request.FILES.get("img")

        if not banner_id or not new_banner_name:
            messages.error(request, "Invalid data received.")
            return redirect("add_banner")

        existing_banner = Banner.objects.filter(title=new_banner_name).exclude(
            id=banner_id
        )
        if existing_banner.exists():
            messages.error(request, "Banner already exists")
            return redirect("add_banner")

        banner = get_object_or_404(Banner, id=banner_id)

        banner.title = new_banner_name

        if new_banner_img:
            banner.image = new_banner_img

        banner.save()

        return redirect("banner")

@never_cache
def show_category(request):
    if request.user.is_authenticated:
        category = Category.objects.all()
        return render(request, "admin/show_category.html", {"category": category})
    else:
        return redirect("home")


@never_cache
def add_category(request):
    if request.user.is_authenticated:
        return render(request, "admin/add_category.html")
    else:
        return redirect("home")


def add_category_action(request):
    if request.method == "POST":
        new_category = request.POST.get("new_category")
        img = request.FILES.get("img")
        existing_category = Category.objects.filter(title=new_category)

        if existing_category.exists():
            messages.error(request, "Category already exists")
            return redirect("add_category")
        else:
            category = Category(title=new_category, image=img)
            category.save()

    return redirect("show_category")


@never_cache
def edit_category(request, cid):
    if request.user.is_authenticated:
        category = Category.objects.get(id=cid)
        return render(request, "admin/edit_category.html", {"category": category})
    else:
        return redirect("home")


def edt_category_action(request):
    if request.method == "POST":
        category_id = request.POST.get("id")
        new_category_name = request.POST.get("newcategory")
        new_category_img = request.FILES.get("img")

        if not category_id or not new_category_name:
            messages.error(request, "Invalid data received.")
            return redirect(
                "add_category"
            )  

        existing_category = Category.objects.filter(title=new_category_name).exclude(
            id=category_id
        )
        if existing_category.exists():
            messages.error(request, "Category already exists")
            return redirect("add_category")

   
        category = get_object_or_404(Category, id=category_id)

        category.title = new_category_name

        if new_category_img:
    
            category.image = new_category_img


        category.save()


        return redirect("show_category")


@never_cache
def show_brand(request):
    if request.user.is_authenticated:
        brand = Brand.objects.all()
        return render(request, "admin/show_brand.html", {"brand": brand})
    else:
        return redirect("home")


@never_cache
def add_brand(request):
    if request.user.is_authenticated:
        return render(request, "admin/add_brand.html")
    else:
        return redirect("home")


def add_brand_action(request):
    if request.method == "POST":
        new_brand = request.POST.get("new_brand")
        existing_brand = Brand.objects.filter(title=new_brand)

        if existing_brand.exists():
            messages.error(request, "Brand already exists")
            return redirect("add_brand")
        else:
            brand = Brand(title=new_brand)
            brand.save()
    return redirect("show_brand")


@never_cache
def edit_brand(request, bid):
    if request.user.is_authenticated:
        brand = Brand.objects.get(id=bid)
        return render(request, "admin/edit_brand.html", {"brand": brand})
    else:
        return redirect("home")


def edt_brand_action(request):
    if request.method == "POST":
        id = request.POST.get("id")
        name = request.POST.get("editbrand")
        existing_brand = Brand.objects.filter(title=name)
        if existing_brand.exists():
            messages.error(request, "Brand already exists")
            return redirect("edit_brand")
        else:
            brand = Brand.objects.get(id=id)
            brand.title = name
            brand.save()
            return redirect("show_brand")



@never_cache
def show_product(request):
    if request.user.is_authenticated:
        products = Product.objects.all()
        return render(request, "admin/show_product.html", {"products": products})
    else:
        return redirect("home")


@never_cache
def admin_view_product(request, uid):
    if request.user.is_authenticated:
        products = Product.objects.get(id=uid)
        return render(request, "admin/view_products.html", {"products": products})
    else:
        return redirect("home")


@never_cache
def edit_product(request, uid):
    if request.user.is_authenticated:
        product = Product.objects.get(id=uid)
        category = Category.objects.all()
        brand = Brand.objects.all()
        return render(
            request,
            "admin/edit_product.html",
            {"product": product, "category": category, "brand": brand},
        )
    else:
        return redirect("home")


def edit_product_action(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            id = request.POST.get("id")
            name = request.POST.get("name")
            description = request.POST.get("description")
            category = request.POST.get("category")
            brand = request.POST.get("brand")
            stock = request.POST.get("stock")
            t_stock = int(stock)
            if t_stock < 0 :
                t_stock = 0
                stock = str(t_stock)
            price1 = request.POST.get("price1")
            price2 = request.POST.get("price2")
            img1 = request.FILES.get("img1")
            img2 = request.FILES.get("img2")
            img3 = request.FILES.get("img3")
            img4 = request.FILES.get("img4")

            product = Product.objects.get(id=id)

            product.title = name
            product.description = description
            product.stock = stock
            try:
                price_float = float(price1)
                if price_float >= 0:
                    product.price = price_float
            except ValueError:
                # Handle invalid input for price1
                pass

            try:
                old_price_float = float(price2)
                if old_price_float >= 0:
                    product.old_price = old_price_float
            except ValueError:
                # Handle invalid input for price2
                pass
            product.category_id = category
            product.brand_id = brand

            if img1 is not None:
                product.image1 = img1
            if img2 is not None:
                product.image2 = img2
            if img3 is not None:
                product.image3 = img3
            if img4 is not None:
                product.image4 = img4

            # Save the updated product
            product.save()
            return redirect("show_product")
        else:
            return redirect("show_product")
    else:
        return redirect("home")
    

    
    
def handle_non_negative(value):
    try:     
        float_value = float(value)
        return max(0, round(float_value))
    except ValueError:
        return 0


@never_cache
def add_product(request):
    if request.user.is_authenticated:
        category = Category.objects.all()
        brand = Brand.objects.all()
        context = {"category": category, "brand": brand}
        return render(request, "admin/add_product.html", context)
    else:
        return redirect("home")


def add_product_action(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            name = request.POST.get("name")
            description = request.POST.get("description")
            brand = request.POST.get("brand")
            category = request.POST.get("category")
            stock = handle_non_negative(request.POST.get("stock"))
            price = handle_non_negative(request.POST.get("price1"))
            old_price = handle_non_negative(request.POST.get("price2"))
            img1 = request.FILES.get("img1")
            img2 = request.FILES.get("img2")
            img3 = request.FILES.get("img3")
            img4 = request.FILES.get("img4")

            product = Product(
                title=name,
                brand_id=brand,
                category_id=category,
                price=str(price),
                old_price=str(old_price),
                stock=str(stock),
                description=description,
                image1=img1,
                image2=img2,
                image3=img3,
                image4=img4,
            )
            product.save()
            return redirect("show_product")
        else:
            return redirect("show_product")
    else:
        return redirect("home")


@never_cache
def show_user(request):
    if request.user.is_authenticated:
        users = User.objects.all().exclude(is_superuser=True)
        return render(request, "admin/show_user.html", {"users": users})
    else:
        return redirect("home")


def customeraction(request, uid):
    if request.user.is_authenticated:
        customer = User.objects.get(id=uid)
        if customer.is_active:
            customer.is_active = False
            print(customer.is_active)
        else:
            customer.is_active = True
        customer.save()
        return redirect("show_user")
    else:
        return redirect("home")


def product_action(request, uid):
    product = Product.objects.get(id=uid)
    if product.active:
        product.active = False
    else:
        product.active = True
    product.save()
    return redirect("show_product")


def category_action(request, cid):
    category = Category.objects.get(id=cid)
    if category.active:
        category.active = False
    else:
        category.active = True
    category.save()
    return redirect("show_category")


def brand_action(request, bid):
    brand = Brand.objects.get(id=bid)
    if brand.active:
        brand.active = False
    else:
        brand.active = True
    brand.save()
    return redirect("show_brand")


def order(request):
    orders = Order.objects.all()
    if request.method == "POST":
        order_id = request.POST.get("orderId")
        selected_status = request.POST.get("status")
        order_item = Order.objects.get(id=order_id)
        order_item.status = selected_status
        order_item.save()
        messages.success(request, "succesfully updated")
    return render(request, "admin/admin_order.html", {"orders": orders})


# views.py
def order_details(request, oid):
    orders = Order.objects.get(id=oid)
    return_request = ReturnRequest.objects.filter(order=orders).first()
    return render(request, "admin/order_details.html", {"orders": orders, 'return_request': return_request})



def coupon_admin(request):
    coupons = Coupon.objects.all()
    return render(request, "admin/coupon_admin.html", {"coupons": coupons})


# views.py in your user-side app


def manage_coupons(request):
    coupons = Coupon.objects.all()
    form = CouponForm()

    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            print('yes it works')
            form.save()
            return redirect('manage_coupons')
        else:
            print(form.errors)

    return render(request, 'admin/manage_coupons.html', {'coupons': coupons, 'form': form})



from django.shortcuts import render, redirect

def edit_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    form = CouponForm(instance=coupon)

    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon edited successfully')
            return redirect('manage_coupons')
        else:
            print(form.errors)
            messages.error(request, 'Error editing coupon. Please correct the errors.')

    return render(request, 'admin/edit_coupon.html', {'form': form, 'coupon': coupon})





def delete_coupon(request, coupon_id):
    print("Inside delete_coupon view")  # Add this line for debugging
    coupon = get_object_or_404(Coupon, id=coupon_id)

    if request.method == 'POST':
        print("Handling POST request")  # Add this line for debugging
        coupon.delete()
        return redirect('manage_coupons')

    return HttpResponse("Invalid request. Use a POST request to delete a coupon.")






def handle_return_request(request, request_id):
    return_request = get_object_or_404(ReturnRequest, id=request_id)

    if request.method == 'POST':
        response = request.POST.get('response')
        if response in ['accepted', 'rejected']:
            return_request.admin_response = response
            return_request.save()

            # Update the order status based on the admin response
            order = return_request.order
            if response == 'accepted':
                order.status = 'returned'
                order.save()

                # Update wallet balance if the return is accepted
                user_wallet = get_object_or_404(Wallet, user=order.user)
                if order.discounted_total is None:
                    transaction_amount = order.total_paid
                else:
                    transaction_amount = order.discounted_total

                # Create a new Wallet_History entry
                wallet_history_entry = Wallet_History.objects.create(
                    wallet=user_wallet,
                    transaction_type='credit',  # Assuming it's a credit since it's a return
                    amount=transaction_amount
                )
                
                # Update wallet balance
                user_wallet.balance += transaction_amount
                user_wallet.save()

                messages.success(request, 'Return request accepted. Wallet balance updated successfully.')
            elif response == 'rejected':
                messages.success(request, 'Return request rejected.')

            return redirect(reverse('order_details', args=[order.id]))

        else:
            messages.error(request, 'Invalid response.')
    else:
        return render(request, 'admin/order_details.html', {'return_request': return_request})




def return_requests_admin(request):
    return_requests = ReturnRequest.objects.filter(admin_response__isnull=True)
    return render(request, 'admin/order_details.html', {'return_requests': return_requests})


