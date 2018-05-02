from django.db import models
from ikea_parser.create_identificator import create_num_identificator
from ikea_parser.models import Product
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

# Create your models here.
class Order(models.Model):
    status = ((0, 'в процессе'), (1, 'новый'),(2, 'не оплачен'), (3, 'задаток'), (4, 'оплачен'), (5, 'выполнен'), (6, 'отменен'))

    unique_identificator = models.CharField(max_length=8, default=create_num_identificator(8), blank=False, null=False)
    order_price = models.FloatField(default=0.0, blank=True, null=True)
    status = models.SmallIntegerField(default=0, blank=True, null=True, choices=status)
    session_key = models.CharField(max_length=256, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True, blank=False, null=False)

class ProductInOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.SmallIntegerField(default=0, blank=False, null=True)
    price_per_one = models.FloatField(default=0.0, blank=True, null=True)
    price = models.FloatField(default=0.0, blank=False, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True, blank=False, null=False)

@receiver(pre_save, sender=ProductInOrder)
def calculate(sender, instance, **kwargs):
    instance.price_per_one = instance.product.price
    instance.price = float(instance.count) * instance.product.price

@receiver(post_save, sender=ProductInOrder)
def calculate_order(sender, instance, **kwargs):
    order = Order.objects.get(id=instance.order.id)
    products_in_order = ProductInOrder.objects.filter(order=order)
    price = 0.0
    for product in products_in_order:
        price += product.price
    order.order_price = price
    order.save()



