from django.db import models
from django.utils.timezone import datetime
from ikea_parser.create_identificator import create_identificator
from django.db.models.signals import post_save
from django.dispatch import receiver
#from admin_panel.views import change_products_price

# Create your models here.

class Coef(models.Model):
    coef = models.FloatField(default=0.0, blank=False, null=False, verbose_name='Коефициент продажи')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    def __str__(self):
        return '%f updated in %s' % (self.coef, self.updated)

@receiver(post_save, sender=Coef)
def change_price(sender, instance, **kwargs):
    change_products_price()
