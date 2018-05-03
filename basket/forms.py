from django.forms import ModelForm
from .models import OrderRegistration

class OrderRegistrationForm(ModelForm):
    model = OrderRegistration
    exclude = ['created', 'updated', 'delivery']