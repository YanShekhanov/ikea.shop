from django import forms
from .models import OrderRegistration, DeliveryMethod, PaymentMethod

class OrderRegistrationForm(forms.ModelForm):
    class Meta:
        model = OrderRegistration
        exclude = ['created', 'updated', 'order']

class DeliveryMethodForm(forms.ModelForm):
    class Meta:
        model = DeliveryMethod
        exclude = ['order']

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        exclude = ['order']
        labels = {
            'payment_method':u'Способ оплаты'
        }