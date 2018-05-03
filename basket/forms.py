from django.forms import ModelForm
from .models import OrderRegistration

class OrderRegistrationForm(ModelForm):
    class Meta:
        model = OrderRegistration
        exclude = ['created', 'updated', 'delivery']