from django.shortcuts import render, redirect, reverse, HttpResponse
from .ikea_parser import *
from .translate import translate
from django.views.generic import TemplateView, FormView, ListView
from .models import *

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
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

# парсинг категорий, подкатегорий
def parse_categories(request):
    parse_categories_()
    return redirect(reverse('home'))

#parse products with lightweight info
def parse_products_articles(request):
    get_sub_and_sub_subcategories()
    return redirect(reverse('home'))

#parse full products informations
def parse_products_information(request):
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
        parse_one_product_information_(product, driver)
        body = driver.find_element_by_tag_name('body')
        body.send_keys(Keys.CONTROL + 't', Keys.CONTROL + Keys.TAB, Keys.CONTROL + 'w') #закрітие старой вкладки и открытие новой
    driver.close()
    return redirect(reverse('home'))

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
    products = ProductImage.objects.all()
    for product in products:
        product.delete()

    '''
    url_ = 'https://www.ikea.com/pl/pl/catalog/products/S59208673/#/S89196678'
    #url = 'https://www.ikea.com/pl/pl/catalog/products/00261295/'
    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1024,768")
    options.add_argument("--no-sandbox")

    browser = webdriver.Chrome(chrome_options=options)
    browser.get(url_)
    html = browser.page_source
    html = requests.get(url_).text
    product_soup = BeautifulSoup(html, 'lxml')

    # -----------------------------------------------------#
    # more models - модели
    parse_models = True
    models_articles_list = []
    models_ = None
    models_to_save = None
    try:
        models_ = product_soup.find('div', id='selectMoremodelsWrapper').find_all('li')
        print(models_)
        print('have models')
    except AttributeError:
        parse_models = False
        print('not exist')

    if parse_models:
        for model in models_:
            models_article = model.get('data-url').split('/')[-2]
            models_articles_list.append(models_article)
        if len(models_articles_list) != 0:
            models_to_save = '#'.join(models_articles_list)'''
    return redirect(reverse('home'))


