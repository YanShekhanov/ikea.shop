from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(ProductInOrder)
admin.site.register(Order)
admin.site.register(OrderRegistration)
admin.site.register(DeliveryMethod)
admin.site.register(PaymentMethod)