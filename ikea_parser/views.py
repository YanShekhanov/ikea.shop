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
    url = 'https://www.ikea.com/pl/pl/catalog/categories/departments/bedroom/Mattresses/?icid=itl|pl|menu|201802131012490682_123'
    #url = 'https://www.ikea.com/pl/pl/catalog/products/00261295/'
    '''options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1024,768")
    options.add_argument("--no-sandbox")

    browser = webdriver.Chrome(chrome_options=options)
    browser.get(url)
    html = browser.page_source
    product_soup = BeautifulSoup(html, 'lxml')'''

    subcategory_request = requests.get(url).text
    subcategory_soup = BeautifulSoup(subcategory_request, 'lxml')
    # проверка на наличие подкатегорий в другом блоке
    sub_subcategories_containers = subcategory_soup.find_all('div', class_='visualNavContainer')
    if sub_subcategories_containers == []:
        sub_subcategories_containers = None
    if sub_subcategories_containers is not None:
        for sub_subcategory_container in sub_subcategories_containers:
            sub_subcategory_block = sub_subcategory_container.find('a', class_='categoryName')
            if sub_subcategory_block == []:
                sub_subcategory_block = None
            if sub_subcategory_block is not None:
                sub_subcategory_url = sub_subcategory_block.get('href')
                sub_subcategory_title = re.sub('\s+', ' ', sub_subcategory_block.text.strip())
                print(sub_subcategory_url)

    return redirect(reverse('home'))


