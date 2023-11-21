from django.contrib import admin
from .models import Category, Brand, Product, Coupon

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

class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'expire_date', 'coupon_type', 'min_purchase_amount']
    search_fields = ['code']

    fieldsets = (
        (None, {
            'fields': ('code', 'discount_type', 'discount_value', 'expire_date', 'coupon_type', 'min_purchase_amount'),
        }),
    )




admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(Coupon, CouponAdmin)
