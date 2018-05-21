from django.forms import ModelForm, Select, Form, CharField, TextInput
from basket.models import Order
from ikea_parser.models import Product

class ChangeStatusForm(ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': Select(attrs={'id':'order-stat'})
        }

class AdminAuthForm(Form):
    username = CharField(label='username', max_length=16, widget=TextInput)
    password = CharField(label='password', max_length=32, widget=TextInput(attrs={'type':'password'}))

class DownloadProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['article_number']