from django.forms import ModelForm, Select, Form, CharField, TextInput
from basket.models import Order

class ChangeStatusForm(ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': Select(attrs={'id':'order-stat'})
        }

class AdminAuthForm(Form):
    username = CharField(label='username', max_length=16, blank=False, widget = TextInput)
    password = CharField(label='password', max_length=32, blank=False, widget = TextInput(attr={'type':'password'}))
