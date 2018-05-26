from django.db import models
from django.utils.timezone import datetime
from ikea_parser.create_identificator import create_identificator
from django.db.models.signals import post_save
from django.dispatch import receiver
from ikea_parser.models import Product
from bs4 import BeautifulSoup
import requests

# Create your models here.

class Coef(models.Model):
    coef = models.FloatField(default=0.0, blank=False, null=False, verbose_name='Коефициент продажи')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    def __str__(self):
        return '%f updated in %s' % (self.coef, self.updated)

@receiver(post_save, sender=Coef)
def change_price(sender, instance, **kwargs):
    products = Product.objects.all()
    for product in products:
        url = 'https://www.ikea.com/pl/pl/catalog/products/%s/' % product.article_number
        product_detail = BeautifulSoup(requests.get(url).text, 'lxml')
        product_price = product_detail.find('span', class_='packagePrice').text.split()[:2]
        if product_price[1] == 'PLN':
            product_price = product_price[0]
        product_price = ''.join(product_price)
        for symbol in product_price:
            if symbol == ' ':
                product_price = ''.join(product_price.split(' '))
        for symbol in product_price:
            if symbol == ',':
                product_price = '.'.join(product_price.split(','))
        product_price = int(round(float(product_price) * instance.coef))
        print(product.with_dot(), product.price, product_price)
