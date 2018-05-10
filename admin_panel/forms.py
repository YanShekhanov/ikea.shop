from django.forms import ModelForm
from basket.models import Order

class ChangeStatusForm(ModelForm):
    class Meta:
        model = Order
        fields = ['status']
