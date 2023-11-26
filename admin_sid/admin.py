from django.contrib import admin
from .models import Category, Brand, Product, Coupon, Banner

# Register your models here.

# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('title')

# class BrandAdmin(admin.ModelAdmin):
#     list_display = ('title')

# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('title',
#                     'category',
#                     'brand',
#                     'image1',
#                     'image2',
#                     'image3',
#                     'image4',
#                     'description',
#                     'price',
#                     'old_price',
#                     'stock')



admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(Banner)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['coupon_name', 'code', 'discount_type', 'discount_value', 'expire_date', 'coupon_type', 'min_purchase_amount']
    search_fields = ['code', 'coupon_name']
    list_filter = ['discount_type', 'coupon_type']
