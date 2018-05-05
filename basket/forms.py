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

class DeliveryInfoForm(forms.Form):
    adres = forms.CharField(max_length=64, label=u'Адрес')
    department_number = forms.CharField(max_length=32, label=u'Номер отделения')

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        exclude = ['order']
        labels = {
            'payment_method':_('Способ оплаты')
        }