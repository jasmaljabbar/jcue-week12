from django.db import models
from django.utils import timezone
# Create your models here.

class Category (models.Model):
    title = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='category',null=True, blank=True)

    def __str__(self):
        return self.title

class Brand (models.Model):
    title = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='brand',null=True, blank=True)
    
    def __str__(self):
        return self.title

class Product (models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    image1 = models.ImageField(upload_to='prodents')
    image2 = models.ImageField(upload_to='prodents',null=True)
    image3 = models.ImageField(upload_to='prodents',null=True)
    image4 = models.ImageField(upload_to='prodents', null=True)
    active = models.BooleanField(default=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=99999,decimal_places=2)
    old_price = models.DecimalField(max_digits=99999,decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.title



class Coupon(models.Model):
    PUBLIC = 'public'
    PRIVATE = 'private'
    COUPON_TYPE_CHOICES = [
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
    ]

    PERCENTAGE = 'percentage'
    FIXED = 'fixed'
    DISCOUNT_TYPE_CHOICES = [
        (PERCENTAGE, 'Percentage'),
        (FIXED, 'Fixed'),
    ]

    coupon_name = models.CharField(max_length=20, blank=True, null=True)
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default=FIXED)
    discount_value = models.DecimalField(max_digits=5, decimal_places=2)
    expire_date = models.DateTimeField()
    coupon_type = models.CharField(max_length=10, choices=COUPON_TYPE_CHOICES, default=PRIVATE)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def is_valid(self, purchase_amount):
        """
        Check if the coupon is still valid based on the expiration date
        and whether the purchase amount meets the minimum requirement.
        """
        return (
            self.expire_date > timezone.now() and
            (self.coupon_type == self.PUBLIC or (self.coupon_type == self.PRIVATE and purchase_amount >= self.min_purchase_amount))
        )

    def calculate_discount(self, total_amount):
        """
        Calculate the discount amount based on the coupon type and value.
        """
        if self.discount_type == self.PERCENTAGE:
            return (self.discount_value / 100) * total_amount
        elif self.discount_type == self.FIXED:
            return min(self.discount_value, total_amount)
        else:
            return 0  # No discount if the type is not recognized

    def __str__(self):
        return self.code
    
    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
