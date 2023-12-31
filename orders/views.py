from django.shortcuts import render
from django.http.response import JsonResponse

from basket.basket import Basket
from .models  import Order, OrderItem

# Create your views here.   

def add(request):
    basket = Basket(request)
    if request.POST.get('action') == 'post':

        order_key = request.POST.get('order_key')
        user_id = request.user.id
        baskettotal = basket.get_total_price()

        # Check if order exists
        
        order = Order.objects.create(user_id=user_id, full_name='name', address1='add1',
                            address2='add2', total_paid=baskettotal, order_key=order_key)
        order_id = order.pk

        for item in basket:
            OrderItem.objects.create(order_id=order_id, product=item['product'], price=item['price'], quantity=item['qty'])

        response = JsonResponse({'success': 'success'})
        return response


def dashboard(request):
    return render(request,'account/dashboard/dashboard.html')