from django.forms import ModelForm

class OrderRegistrationForm(ModelForm):
    model = OrderRegistration
    exclude = ['created', 'updated', 'delivery']