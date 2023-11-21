from django.shortcuts import get_object_or_404, render, redirect
from decimal import Decimal
from orders.models import Order, OrderItem
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Category 
# Coupon
from django.contrib import messages
from django.http import HttpResponse


# Create your views here.
@never_cache
def admin_dsh(request):
    if request.user.is_authenticated:
        return render(request, "admin/admin_dsh.html")
    else:
        return redirect("home")


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

            product.name = name
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


def order_details(request, oid):
    orders = Order.objects.get(id=oid)
    return render(request, "admin/order_details.html", {"orders": orders})


def coupon_admin(request):
    coupons = Coupon.objects.all()
    return render(request, "admin/coupon_admin.html", {"coupons": coupons})


# def add_coupon_admin(request):
#     if request.method == "POST":
#         coupon_name = request.POST.get("coupon_name")
#         coupon_code = request.POST.get("code")
#         discount = Decimal(request.POST.get("discount"))
#         expiration_date = request.POST.get("expire_date")
#         coupon_type = request.POST.get("coupon_type")
#         min_purchase_amount = Decimal(request.POST.get("min_purchase_amount"))

#         new_coupon = Coupon(
#             coupon_name=coupon_name,
#             code=coupon_code,
#             discount=discount,
#             expire_date=expiration_date,
#             coupon_type=coupon_type,
#             min_purchase_amount=min_purchase_amount,
#         )
#         new_coupon.save()

#     return render(request, "admin/add_coupon.html")




# def edit_coupon(request, id):
#     coupon = get_object_or_404(Coupon, id=id)
#     return render(request, "admin/edit_coupon.html", {"coupon": coupon})
    






# def update_coupon(request):
#     if request.method == "POST":
#         id = request.POST.get("id")
#         try:
#             coupon = get_object_or_404(Coupon, id=id)
            
#             # Update the coupon fields based on the form data
#             coupon.coupon_name = request.POST.get("coupon_name")
#             coupon.code = request.POST.get("code")
#             coupon.discount = Decimal(request.POST.get("discount"))
#             coupon.expire_date = request.POST.get("expire_date")
#             coupon.coupon_type = request.POST.get("coupon_type")
#             coupon.min_purchase_amount = Decimal(request.POST.get("min_purchase_amount"))

#             # Save the updated coupon
#             coupon.save()
            
#             return redirect("coupon_admin")
#         except Coupon.DoesNotExist:
#             # Handle the case where the coupon with the given id does not exist.
#             pass

