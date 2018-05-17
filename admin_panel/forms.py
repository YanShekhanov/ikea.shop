from django.forms import ModelForm, Select
from basket.models import Order

class ChangeStatusForm(ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': Select(attrs={'id':'order-stat'})
        }
