from django.db import models
from ikea_parser.create_identificator import create_num_identificator
from ikea_parser.models import Product
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

# Create your models here.
class Order(models.Model):
    status = ((0, 'в процессе'), (1, 'не оплачен'), (2, 'задаток'), (3, 'оплачен'), (4, 'выполнен'), (5, 'отменен'))
    unique_identificator = models.CharField(max_length=8, default=create_num_identificator(8), blank=False, null=False)
    order_price = models.IntegerField(default=0, blank=True, null=True)
    status = models.SmallIntegerField(default=0, blank=True, null=True, choices=status)
    session_key = models.CharField(max_length=256, blank=False, null=False)
    first_registration = models.DateTimeField(blank=True, null=True, verbose_name='Дата регистрации заказа')
    created = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True, blank=False, null=False)

@receiver(pre_save, sender=Order)
def first_order_registration(sender, instance, **kwargs):
    try:
        status_before_saving = Order.objects.get(id=instance.id).status
        if status_before_saving == 0 and instance.status == 1:
            instance.first_registration = 0
    except Order.DoesNotExist:
        pass
        


class ProductInOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.SmallIntegerField(default=0, blank=False, null=True)
    price_per_one = models.IntegerField(default=0, blank=True, null=True)
    price = models.IntegerField(default=0, blank=False, null=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(default=timezone.now(), editable=False)

@receiver(pre_save, sender=ProductInOrder)
def calculate(sender, instance, **kwargs):
    instance.price_per_one = instance.product.price
    instance.price = instance.count * instance.product.price

@receiver([post_save, post_delete], sender=ProductInOrder)
def calculate_order(sender, instance, **kwargs):
    order = Order.objects.get(id=instance.order.id)
    products_in_order = ProductInOrder.objects.filter(order=order)
    price = 0
    for product in products_in_order:
        price += product.price
    order.order_price = price
    order.save()

class OrderRegistration(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name='order')
    name = models.CharField(max_length=32, default=None, blank=False, null=True, verbose_name='имя')
    second_name = models.CharField(max_length=32, default=None, blank=False, null=True, verbose_name='отчество')
    sorname = models.CharField(max_length=32, default=None, blank=False, null=True, verbose_name='фамилия')
    phone = models.CharField(max_length=17, default=None, blank=False, null=True, verbose_name='телефон')
    email = models.EmailField(max_length=64, default=None, blank=False, null=True, verbose_name='email')
    attentions = models.TextField(blank=True, default=None, null=True, verbose_name='дополнительно')
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(default=timezone.now(), editable=False)

class DeliveryMethod(models.Model):
    methods = ((0, 'Новая почта'), (1, 'Новая почта (курьер)'), (2, 'Delivery'), (3, 'Delivery (курьер)'),
               (4, 'УкрПочта'), (5, 'УкрПочта (курьер)'), (6, 'Интайм'), (7, 'Интайм (курьер)'))
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name='order')
    delivery_method = models.SmallIntegerField(choices=methods, default=None, blank=False, null=True)
    city = models.CharField(max_length=32, default=None, blank=False, null=True)
    adres = models.CharField(max_length=64, default=None, blank=True, null=True)
    department_number = models.SmallIntegerField(default=0, blank=True, null=True)

    def method_readable(self):
        if self.delivery_method == 1 or self.delivery_method == 3 or self.delivery_method == 5 or self.delivery_method ==7:
            return '%s, адрес: %s, %s ' % (dict(DeliveryMethod.methods)[self.delivery_method], self.city, self.adres )
        else:
            return '%s, адрес: %s, %s ' % (dict(DeliveryMethod.methods)[self.delivery_method], self.city, str(self.department_number))

class PaymentMethod(models.Model):
    methods = ((0, 'Полная оплата'), (1, 'Частичная оплата'), (2, 'Наложенный платеж'))
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name='order')
    payment_method = models.SmallIntegerField(choices=methods, blank=False, null=True, default=None)
    amount = models.IntegerField(blank=True, null=True, default=0)

    def method_readable(self):
        if self.payment_method == 0 or self.payment_method == 2:
            return dict(PaymentMethod.methods)[self.payment_method]
        elif self.payment_method == 1:
            return '%s, сумма: %i' % (dict(PaymentMethod.methods)[self.payment_method], self.amount)




