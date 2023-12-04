# forms.py in your user-side app
from django.core.validators import MinValueValidator
from django import forms
from .models import Coupon,Category


class CouponForm(forms.ModelForm):
    discount_value = forms.DecimalField(
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    class Meta:
        model = Coupon
        fields = '__all__'
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'expire_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_coupon_name(self):
        coupon_name = self.cleaned_data['coupon_name']
        if coupon_name and coupon_name.strip() == '':
            raise forms.ValidationError("Coupon name cannot be just spaces.")
        return coupon_name

class EditCouponForm(forms.ModelForm):
    discount_value = forms.DecimalField(
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    class Meta:
        model = Coupon
        fields = ['coupon_name', 'code', 'discount_type', 'discount_value', 'expire_date', 'coupon_type', 'min_purchase_amount']

    def clean_coupon_name(self):
        coupon_name = self.cleaned_data['coupon_name']
        if coupon_name and coupon_name.strip() == '':
            raise forms.ValidationError("Coupon name cannot be just spaces.")
        return coupon_name


class ReturnReasonForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea)




class AdminReturnResponseForm(forms.Form):
    response = forms.ChoiceField(choices=[('accepted', 'Accept'), ('rejected', 'Reject')],
                                 widget=forms.Select(attrs={'class': 'form-control'}),
                                 label='Admin Response')


class AddBannerForm(forms.Form):
    new_banner = forms.CharField(max_length=255, required=True)
    link = forms.URLField(required=True)
    img = forms.ImageField(required=True)


from django import forms
from .models import Banner

class EditBannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'link', 'image']



class CategoryForm(forms.Form):
    new_category = forms.CharField(max_length=255, required=True)
    img = forms.ImageField(required=True)


class EditCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'image']


class BrandForm(forms.Form):
    new_brand = forms.CharField(label='New Brand', max_length=100, required=True)


class EditBrandForm(forms.Form):
    edit_brand = forms.CharField(label='Edit Brand', max_length=100, required=True)

# forms.py


# forms.py
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'category', 'brand', 'stock', 'price', 'old_price', 'image1', 'image2', 'image3', 'image4']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        
        # Set required attribute to False for optional image fields
        self.fields['image2'].required = False
        self.fields['image3'].required = False
        self.fields['image4'].required = False

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean_old_price(self):
        old_price = self.cleaned_data.get('old_price')
        if old_price and old_price <= 0:
            raise forms.ValidationError("Old Price must be greater than zero.")
        return old_price

    def clean(self):
        cleaned_data = super().clean()
        stock = cleaned_data.get('stock')
        price1 = cleaned_data.get('price1')
        price2 = cleaned_data.get('price2')

        if stock is not None and stock < 0:
            self.add_error('stock', 'Stock cannot be negative.')

        if price1 is not None and price1 < 0:
            self.add_error('price1', 'Price 1 cannot be negative.')

        if price2 is not None and price2 < 0:
            self.add_error('price2', 'Price 2 cannot be negative.')
