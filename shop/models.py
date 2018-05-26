from django.db import models
from django.utils.timezone import datetime
from ikea_parser.create_identificator import create_identificator
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from ikea_parser.models import Product
from bs4 import BeautifulSoup
import requests
from admin_panel.models import Process

# Create your models here.

class Coef(models.Model):
    coef = models.FloatField(default=0.0, blank=False, null=False, verbose_name='Коефициент продажи')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    def __str__(self):
        return '%f updated in %s' % (self.coef, self.updated)

@receiver(post_save, sender=Coef)
def change_price(sender, instance, **kwargs):
    created_process = Process.objects.create(process_name='change_prices', time_start=datetime.now())
    try:
        print('all: ', Product.objects.all())
        print('with coef %f: ' % instance.coef, len(Product.objects.filter(price_coef=instance.coef)))
        products = Product.objects.exclude(change_price_process=True, price_coef=instance.coef)
        print('to change% ', len(products))
        with open('../logs/errors_change_price.log', 'a') as to_write:
            for product in products:
                url = 'https://www.ikea.com/pl/pl/catalog/products/%s/' % product.article_number
                product_detail = BeautifulSoup(requests.get(url).text, 'lxml')
                try:
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
                    product.price = product_price
                    product.price_coef = instance.coef
                    product.change_price_process = True
                    product.save()
                except AttributeError:
                    to_write.write('%s error \n' % product.with_dot())
            created_process.time_end = datetime.now()
            created_process.executable = False
            created_process.save()
            to_write.close()
    except:
        created_process.time_end = datetime.now()
        created_process.executable = False
        created_process.save()

