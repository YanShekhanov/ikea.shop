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

def parse_products_articles(request):
    get_sub_and_sub_subcategories()
    return redirect(reverse('home'))

def parse_products_information(request):
    pathlib.Path(os.path.join(MEDIA_ROOT, 'products/') + '250px/').mkdir(parents=True, exist_ok=True)
    pathlib.Path(os.path.join(MEDIA_ROOT, 'products/') + '500px/').mkdir(parents=True, exist_ok=True)
    pathlib.Path(os.path.join(MEDIA_ROOT, 'products/') + '2000px/').mkdir(parents=True, exist_ok=True)
    pathlib.Path(os.path.join(MEDIA_ROOT, 'products/') + 'icons/').mkdir(parents=True, exist_ok=True)
    print('Общее количество продуктов в БД = %i' % len(Product.objects.all()))
    print('Количество готовых продуктов = %i' % len(Product.objects.filter(is_parsed=True)))
    print('Количество продуктов к парсингу = %i' % len(Product.objects.exclude(is_parsed=True)))

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

def test(request):
    articles = Product.objects.filter(article_number='20309258')
    for article in articles:
        article.delete()
   ''' url = 'https://www.ikea.com/pl/pl/catalog/products/S79248041/?query=S79248041'
    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1024,768")
    options.add_argument("--no-sandbox")

    browser = webdriver.Chrome(chrome_options=options)
    browser.get(url)
    html = browser.page_source
    product_soup = BeautifulSoup(html, 'lxml')

    key_feautures = None
    try:
        key_feautures = product_soup.find('div', id='custBenefit').text
    except AttributeError:
        key_feautures = None

    try:
        care_instructions = product_soup.find('div', id='careInstructionsPart').find('div', id='careInst').text
    except AttributeError:
        care_instructions = None

    # -----------------------------------------------------#
    # environment materials - материалы
    materials = None
    try:
        environment_button = browser.find_element_by_id('envAndMatTab')
        environment_button.click()
        html = browser.page_source
        product_soup = BeautifulSoup(html, 'lxml')
        materials = product_soup.find('div', id='custMaterials').contents
        materials_list = []
        for material in materials:
            if isinstance(material, str):
                materials_list.append(material)
    except NoSuchElementException:
        pass

    good_to_know = None
    try:
        good_to_know = product_soup.find('div', id='goodToKnowPart').find('div', id='goodToKnow').text
    except AttributeError:
        good_to_know = None

    print(good_to_know)'''
    return redirect(reverse('home'))


