from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from acount.models import User_profile
from orders.models import Order
from django.utils import timezone
from .utils import send_otp
import pyotp
from payment.models import Address
from django.db.models import Q
from datetime import datetime
from django.views.decorators.cache import never_cache
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from admin_sid.models import *
from basket.models import Cart, CartItem , WishItem
from .models import Wallet, Wallet_History
from django.http import JsonResponse
from .forms import UserProfileForm
# Create your views here.

from django.contrib.auth.hashers import check_password



def home(request):
    user = request.user
    product = Product.objects.all()[:12]
    active_banners = Banner.objects.filter(is_active=True)
    best_sellers = Product.objects.filter(active=True).order_by('-best_sellers')[:4]

    for p in product:
        try:
            category_offers = ProductOffer.objects.filter(category=p.category)

            if category_offers.exists():
                # Assuming you want to take the first offer
                category_offer = category_offers.first()

                if not category_offer.is_valid_for_category():
                    p.price = p.old_price
                    p.old_price = p.discount_price
                    p.discount_price = 0
                    p.save()
        except ProductOffer.DoesNotExist:
            # No category offer found, handle accordingly
            pass

    return render(request, "app/home.html", {"product": product, 'active_banners': active_banners, 'best_sellers': best_sellers})




def sign_up(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        return render(request, "app/usersignup.html")


def signup_perform(request):
    if request.method == "POST":
        first_name = request.POST["name"]
        email = request.POST["email"]
        username = request.POST["username"]
        password_1 = request.POST["password_1"]
        password_2 = request.POST["password_2"]
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already exists")
            return redirect("sign_up")
        elif User.objects.filter(username=username).exists():
            messages.error(request, ":Username is already exists")
            return redirect("sign_up")
        else:
            if password_1 == password_2:
                request.session["mail"] = email
                request.session["user_data"] = {
                    "username": username,
                    "first_name": first_name,
                    "email": email,
                    "password": password_1,
                }
                send_otp(request)
                return redirect("otp")
            else:
                messages.error(request, "Password doesn't match")
                return redirect("sign_up")
    else:
        messages.error(request, "Method not allowed")
        return redirect("sign_up")


def otp(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        return render(request, "app/otp.html")


def otp_perform(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        user_data = request.session.get("user_data")
        otp_key = request.session.get("otp_key")
        otp_valid = request.session.get("otp_valid")
        if otp_key and otp_valid is not None:
            valid_otp = datetime.fromisoformat(otp_valid)
            print(otp_valid)
            if valid_otp > datetime.now():
                totp = pyotp.TOTP(otp_key, interval=60)
                if totp.verify(otp):
                    user = User.objects.create_user(**user_data)
                    request.session["user"] = user.email
                    login(request, user)
                    clear_session(request)
                    return redirect("user_login")
                else:
                    messages.error(request, "OTP invalid")
                    return redirect("otp")
            else:
                clear_session(request)
                messages.error(request, "OTP expired")
                return redirect("sign_up")
        else:
            clear_session(request)
            messages.error(request, "Didnt get any otp")
            return redirect("sign_up")
    else:
        clear_session(request)
        return redirect("sign_up")


def clear_session(request):
    key = ["otp_key", "otp_valid", "user_data", "mail"]
    for key in key:
        if key in request.session:
            del request.session[key]


def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        return render(request, "app/userlogin.html")


def login_perform(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        if User.objects.filter(username=username).exists():
            if User.objects.get(username=username).is_active:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if user.is_superuser:
                        login(request, user)
                        return redirect("dashboard")
                    else:
                        login(request, user)
                        return redirect("home")
                else:
                    messages.error(request, "Username or password is incorrect")
                    return redirect("user_login")
            else:
                messages.error(request, "User is Blocked")
                return redirect("user_login")
        else:
            messages.error(request, "User doesn't exists")
            return redirect("user_login")
    else:
        return redirect("user_login")


@never_cache
def home_perform(request):
    if not request.user.is_authenticated:
        return render(request, "app/userlogin.html")
    else:
        return redirect("home")


@never_cache
def category_search(request, uid):
    user = request.user
    product = Product.objects.filter(category=uid)
    for p in product:
        if user.is_authenticated:
            p.in_basket = CartItem.objects.filter(user=user, product=p).exists()
            p.in_wishlist_count = WishItem.objects.filter(user=user, product=p).exists()
        else:
            p.in_basket = False
            p.in_wishlist_count = False
    return render(request, "app/category_page.html", {"product": product})


def search(request):
    query = request.GET.get("query")
    if query:
        product = Product.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).exclude(active=False)
        return render(request, "app/category_page.html", {"product": product})


def price_filter(request):
    product = Product.objects.none()  # Initialize with an empty queryset

    if request.method == "POST":  # Change this to GET if you are making a GET request
        min_price = request.POST.get("min_price")
        max_price = request.POST.get("max_price")

        if min_price and max_price:
            try:
                min_price = float(min_price)
                max_price = float(max_price)
            except ValueError:
                error_message = "Invalid price values"
                return render(request, "app/error_page.html", {'error_message': error_message})

            # Filter products based on price range
            
            product = Product.objects.filter(
                Q(price__gte=min_price) & Q(price__lte=max_price)
            ).exclude(active=False)

    return render(request, "app/category_page.html", {"product": product})


@never_cache
def view_product(request, pid):
    vi_product = Product.objects.get(id=pid)
    return render(request, "app/view_product.html", {"vi_product": vi_product})


@login_required
def userprofile(request):
    if request.user.is_authenticated:
        try:
            order = Order.objects.filter(user=request.user)
            user_profile = User_profile.objects.get(user=request.user)
        except User_profile.DoesNotExist:
            user_profile = None

        return render(
            request,
            "app/user_profile.html",
            {"user_profile": user_profile, "order": order},
        )
    else:
        return redirect("home")





@login_required
def edit_profile(request):
    user_profile = User_profile.objects.get_or_create(user=request.user)[0]
    form = UserProfileForm(instance=user_profile)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('userprofile')
        else:
            messages.error(request, 'Error updating profile. Please correct the errors.')

    return render(request, 'app/edit_profile.html', {'form': form, 'user_profile': user_profile})






@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        # Check if the old password matches the current password
        if not check_password(old_password, request.user.password):
            return JsonResponse({'message': 'Incorrect old password.'}, status=400)

        # Check if the new password contains spaces
        if ' ' in new_password:
            return JsonResponse({'message': 'New password cannot contain spaces.'}, status=400)

        # Add additional password validation rules if needed
        # For example, you can check for minimum length or complexity requirements

        # Update the user's password
        request.user.set_password(new_password)
        request.user.save()

        # Authenticate the user with the new password
        user = authenticate(username=request.user.username, password=new_password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Password changed successfully.'})
        else:
            return JsonResponse({'message': 'Error authenticating user with new password.'}, status=400)

    return JsonResponse({'message': 'Invalid request.'}, status=400)



@login_required
def view_wallet(request):
    try:
        wallet = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=request.user, balance=0)

    
    wallet_history = Wallet_History.objects.filter(wallet__user=request.user)

    return render(request, 'app/wallet.html', {'wallet': wallet, 'wallet_history': wallet_history})




@login_required
def add_funds(request):
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        wallet = Wallet.objects.get(user=request.user)
        wallet.balance += amount
        wallet.save()
        return redirect('view_wallet')

    return render(request, 'wallet/add_funds.html')



def log_out(request):
    request.session.flush()
    logout(request)
    return redirect("home")

def coupon(request):
    coupons = Coupon.objects.filter(coupon_type='public')
    user = request.user
    return render(request, 'app/user_coupon.html', {'coupons': coupons,
                                                    'user_is':user})


def coupon_action(request):
    billing_address = Address.objects.filter(user=request.user)
    if request.method == 'POST':
        coupon_code = request.POST.get("coupon_code")
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        total_paid = cart.get_total_price()
        shipping_price = cart.get_shipping_price()
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            coupons = Coupon.objects.filter(Q(coupon_type='public') &
                                            Q(expire_date__gte=timezone.now()) &
                                            Q(min_purchase_amount__lte=cart.get_total_price()) & 
                                            ~Q(user=request.user))
            request.session['coupon-code'] = coupon_code
        except Coupon.DoesNotExist:
            return render(request, "payment/address.html", {"message": "Invalid coupon code"}, status=400)


        if coupon.is_valid(total_paid) and not coupon.flag:
            discount = coupon.calculate_discount(total_paid)
            discounted_total = total_paid - discount
            request.session['discounted_total'] = float(discounted_total)
            coupon.save()  


            return render(request, "payment/address.html", {"discounted_total": discounted_total,"billing_address":billing_address,'coupons':coupons,"shipping_price": shipping_price,})
        else:
            return render(request, "payment/address.html", {"message": "Coupon is not valid for this purchase","billing_address":billing_address}, status=400)

    return render(request, "payment/address.html", {"message": "Invalid request method","billing_address":billing_address}, status=400)


def remove_coupon(request):
    return redirect('payment:BasketView')








# ------------------------------forgot_password-----------


def forget_password_action(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.get(email=email)

        if user:
            request.session["id"] = user.pk
            request.session["mail"] = email
            send_otp(request)
            return redirect("for_otp")
        else:
            messages.error(request, "User with the given email does not exist.")
            return render(request, "app/userlogin.html")

    return render(request, "app/userlogin.html")


def for_otp(request):
    return render(request, "app/forgetOtp.html")


def forget_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        otp_key = request.session.get("otp_key")
        otp_valid = request.session.get("otp_valid")

        print("Entered OTP:", otp)
        print("Stored OTP Key:", otp_key)
        print("Stored OTP Validity:", otp_valid)

        if otp_key and otp_valid is not None:
            valid_otp = datetime.fromisoformat(otp_valid)
            if valid_otp > datetime.now():
                totp = pyotp.TOTP(otp_key, interval=60)
                if totp.verify(otp):
                    print("OTP Verified Successfully!")
                    return redirect("new_password")
                else:
                    messages.error(request, "Invalid Otp")
                    return redirect("for_otp")
            else:
                clear_session(request)
                messages.error(request, "Otp expired")
                return redirect("for_otp")
        else:
            clear_session(request)
            messages.error(request, "Didn't get any otp")
            return redirect("for_otp")

    return redirect("for_otp")


def forgot_password(request):
    id = request.session.get("id")
    print("User ID from session:", id)
    return render(request, "app/forgetpassword.html")



def new_password(request):
    if request.method == "POST":
        password_1 = request.POST.get("password_1")
        password_2 = request.POST.get("password_2")

        if password_1 == password_2:
            email = request.session.get("mail")
            user = User.objects.get(email=email)
            hashed_password = make_password(password_1)
            user.password = hashed_password
            user.save()

            # Clear the session
            request.session.clear()

            return redirect("user_login")
        else:
            messages.error(request, "password is not match")
            return render(request, "app/newpassword.html")

    return render(request, "app/newpassword.html")
