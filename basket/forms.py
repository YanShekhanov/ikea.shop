from django import forms
from .models import OrderRegistration

class OrderRegistrationForm(forms.ModelForm):
    methods = ((0, 'Новая почта'),(1, 'Delivery'),(2, 'УкрПочта'),(3, 'Интайм'))
    method = forms.CharField(widget=forms.Select(choices=methods),label='Почта')
    class Meta:
        model = OrderRegistration
        exclude = ['created', 'updated', 'delivery', 'order']

