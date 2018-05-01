from django.contrib import admin
from .models import *
# Register your models here.

class ProductInOrderInline(admin.StackedInline):
    model = ProductInOrder
    exclude = ('order', 'product')

class OrderAdmin(admin.ModelAdmin):
    inlines = [ProductInOrderInline]
    extra = 1

admin.site.register(OrderAdmin)