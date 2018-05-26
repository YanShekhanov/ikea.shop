from django.forms import ModelForm, Select, Form, CharField, TextInput, NumberInput
from basket.models import Order, PaymentMethod
from ikea_parser.models import Product
#from shop.models import Coef
from shop.models import *

class ChangeStatusForm(ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': Select(attrs={'id':'order-stat'})
        }

class ChangePaymentForm(ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['payment_method', 'amount']


class AdminAuthForm(Form):
    username = CharField(label='username', max_length=16, widget=TextInput)
    password = CharField(label='password', max_length=32, widget=TextInput(attrs={'type':'password'}))

class DownloadProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['article_number']

class SearchOrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['unique_identificator']
        widgets = {
            'unique_identificator': NumberInput(attrs={'type':'number'})
        }

class ChangeCoefForm(ModelForm):
    class Meta:
        model = Coef
        fields = ['coef']