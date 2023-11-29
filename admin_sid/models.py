from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User 
# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='category', null=True, blank=True)

    def __str__(self):
        return self.title

class Brand(models.Model):
    title = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='brand', null=True, blank=True)

    def __str__(self):
        return self.title

class Variant(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)  # Optional additional data
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

class Product(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    variants = models.ManyToManyField(Variant, blank=True)
    image1 = models.ImageField(upload_to='prodents')
    image2 = models.ImageField(upload_to='prodents', null=True)
    image3 = models.ImageField(upload_to='prodents', null=True)
    image4 = models.ImageField(upload_to='prodents', null=True)
    active = models.BooleanField(default=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=99999, decimal_places=2)
    old_price = models.DecimalField(max_digits=99999, decimal_places=2)
    stock = models.IntegerField()
    best_sellers = models.IntegerField(default=0)

    def __str__(self):
        return self.title

best_sellers = Product.objects.filter(active=True).order_by('-best_sellers')[:4]

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    flag = models.BooleanField(default=False) 
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default=FIXED)
    discount_value = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField(default=timezone.now, blank=True)
    expire_date = models.DateTimeField()
    coupon_type = models.CharField(max_length=10, choices=COUPON_TYPE_CHOICES, default=PRIVATE)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def is_valid_for_user(self, user, total_paid):
        return self.is_valid(total_paid) and user not in self.user.all()
    
    
    def save(self, *args, **kwargs):
        if not self.start_date:
            self.start_date = timezone.now()

        
        super().save(*args, **kwargs)

    def is_valid(self, purchase_amount):
        time_now = timezone.now() + timedelta(hours=5, minutes=30)

        date_condition = self.start_date <= time_now <= self.expire_date
        amount_condition = (
            self.coupon_type == self.PUBLIC or 
            (self.coupon_type == self.PRIVATE and purchase_amount >= self.min_purchase_amount)
        )


        return date_condition and amount_condition

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



class Banner(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

