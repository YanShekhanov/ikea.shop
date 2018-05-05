from django import forms
from .models import OrderRegistration, DeliveryMethod, PaymentMethod

class OrderRegistrationForm(forms.ModelForm):
    class Meta:
        model = OrderRegistration
        exclude = ['created', 'updated', 'order']

class PostMethod(forms.Form):
    class Meta:
        model = DeliveryMethod
        exclude = ['order']

class PayMethod(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        exclude = ['order']