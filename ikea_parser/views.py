from django.shortcuts import render, redirect, reverse, HttpResponse
from .ikea_parser import *
from .translate import translate
from django.views.generic import TemplateView, FormView, ListView
from .models import *

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from threading import Thread
from app.settings import MEDIA_ROOT
# Create your views here.

#--------------------
class HomePage(ListView):
    template_name = 'home_page.html'
    model = Product
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super(HomePage, self).get_context_data(**kwargs)
        context['productsImages'] = ProductImage.objects.all()
        return context

class ParserProcess(Thread):
    def __init__(self, name, request):
        Thread.__init__(self)
        self.name = name
        self.request = request

    def run(self):
        print('parser start with name %s' % self.name)
        print('Products count = %i' % len(Product.objects.all()))
        print('Ready product = %i' % len(Product.objects.filter(is_parsed=True)))
        print('products to parse = %i' % len(Product.objects.exclude(is_parsed=True)))

        try:
            products = Product.objects.filter(is_parsed=False)
        except Product.DoesNotExist:
            return HttpResponse(status=404)

        options = Options()
        options.add_argument("--headless")
        options.add_argument("window-size=1024,768")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(chrome_options=options)
        for product in products:
            print(product.with_dot())
            parse_one_product_information_(product, driver)
            body = driver.find_element_by_tag_name('body')
            body.send_keys(Keys.CONTROL + 't', Keys.CONTROL + Keys.TAB, Keys.CONTROL + 'w')  # закрітие старой вкладки и открытие новой
        driver.close()



# парсинг категорий, подкатегорий
def parse_categories(request):
    parse_categories_()
    return redirect(reverse('home'))

#parse products with lightweight info
def parse_products_articles(request):
    get_sub_and_sub_subcategories()
    return redirect(reverse('home'))

#parse full products informations
#asinc
def parse_products_information(request):
    parser = ParserProcess('parser', request)
    parser.start()
    return redirect(reverse('catalogue'))

#parse rooms
def parse_rooms_examples(request):
    if request.method=='POST':
        pass
    if request.method=='GET':
        rooms_places = RoomPlace.objects.all()
        for room_place in rooms_places:
            parse_examples(room_place)
        return redirect(reverse('home'))


#УДАЛЕНИЕ
def delete_images(request):
    images = ProductImage.objects.all()
    for image in images:
        image.delete()
    return redirect(reverse('home'))

def delete_categories(request):
    categories = Category.objects.all()
    for category in categories:
        category.delete()
    return redirect(reverse('home'))

def delete_products(request):
    deleted_products = 0
    try:
        products = Product.objects.all()
        for product in products:
            product.delete()
            deleted_products+=1
        print('Все продукты были удалены (%i)' % deleted_products)
    except Product.DoesNotExist:
        print('Продукты не найдены')
        return HttpResponse(status=404)
    return redirect(reverse('home'))

from bs4 import BeautifulSoup
import requests
def test(request):
    products = Product.objects.filter(article_number=30221043)
    for product in products:
        product.delete()

    '''itter=0
    for product in Product.objects.all():
        if product.unique_identificator == '':
            product.unique_identificator = create_identificator(8)
            product.save()
            print('for article %s created identificator %s' % (product.with_dot(), product.unique_identificator))
            itter += 1
    print('changed = %i' % itter)
    
    room_places = RoomPlace.objects.all()
    for place in room_places:
        parse_examples(place)'''
    return redirect(reverse('home'))


