from django.db import models
from decimal import Decimal
from django.conf import settings
from admin_sid.models import Product

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order_user', null=True, blank=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    address1 = models.CharField(max_length=250, null=True, blank=True)
    address2 = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    post_code = models.CharField(max_length=20, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order_key = models.CharField(max_length=200, null=True, blank=True)
    billing_status = models.CharField(max_length=10,)

    # New field for order status
    ORDER_STATUS_CHOICES = [
        ('confirmed', 'Order Confirmed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        # Add more statuses as needed
    ]

    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='confirmed')

    class Meta:
        ordering = ('-created',)
    
    def __str__(self):
        return f"{self.created} - {self.status}"

    @classmethod
    def get_user_order_status(cls, user):
        """
        Get the status of the latest order for a specific user.
        """
        latest_order = cls.objects.filter(user=user).order_by('-created').first()
        if latest_order:
            return latest_order.status
        return None


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              related_name='items',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product,
                                related_name='order_items',
                                on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)
