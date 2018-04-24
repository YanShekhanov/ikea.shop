from django.db import models
from ikea_parser.create_identificator import create_identificator
from ikea_parser.models import Product

# Create your models here.
class Order(models.Model):
    unique_identificator = models.CharField(max_length=16, default=create_identificator(16), blank=False, null=False)
    order_price = models.FloatField(default=0.0, blank=True, null=True)
    status = models.SmallIntegerField(default=0, blank=True, null=True)
    #session_key = models.CharField()
    created = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True, blank=False, null=False)


class ProductInOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.SmallIntegerField(default=0, blank=False, null=True)
    price = models.FloatField(default=0.0, blank=False, null=True)