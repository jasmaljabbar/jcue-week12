# forms.py in your user-side app

from django import forms
from .models import Coupon

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = '__all__'
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'expire_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class EditCouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['coupon_name', 'code', 'discount_type', 'discount_value', 'expire_date', 'coupon_type', 'min_purchase_amount']



class ReturnReasonForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea)


# forms.py
from django import forms

class AdminReturnResponseForm(forms.Form):
    response = forms.ChoiceField(choices=[('accepted', 'Accept'), ('rejected', 'Reject')],
                                 widget=forms.Select(attrs={'class': 'form-control'}),
                                 label='Admin Response')
