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

    # проверка на наличие подподкатегории
    options_dict = {'row-first row': {'tag': 'div', 'find': 'img-slot', 'code': 1},
                    'row-second row': {'tag': 'div', 'find': 'img-slot', 'code': 1},
                    'visualNavContainer': {'tag': 'a', 'find': 'categoryName', 'code': 2},
                    }
    print(options_dict.keys())
    for key in options_dict.keys():
        print(key)
        option = options_dict.get(key)
        tag = option.get('tag')
        find = option.get('find')
        code = option.get('code')

        subcategory_request = requests.get(url).text
        subcategory_soup = BeautifulSoup(subcategory_request, 'lxml')
        sub_subcategories_container = subcategory_soup.find('div', class_=key)
        if sub_subcategories_container == []:
            sub_subcategories_container = None

        if sub_subcategories_container is not None:
            print('найдено')
            sub_subcategories = sub_subcategories_container.find_all(tag, class_=find)
            print(sub_subcategories)
            if code == 1:
                print('code = 1')
                if sub_subcategories == []:
                    sub_subcategories = None
                if sub_subcategories is not None:
                    print(sub_subcategories)
                    print('YES " %s " ' % subcategory_url)
                    subcategory_created.have_sub_subcategory = True
                    subcategory_created.save()
                    for sub_subcategory in sub_subcategories:
                        sub_subcategory_title = re.sub('\s+', ' ', sub_subcategory.find('a').text.strip())
                        sub_subcategory_url = sub_subcategory.find('a').get('href')
            if code == 2:
                print('code=2')
                for category in sub_subcategories:
                    url = category.get('href')
                    title = category.text
                    print(url, title)


    # -----------------------------------------------------#
    '''more models - модели
    parse_models = True
    models_articles_list = []
    #models = None
    models_ = None
    models_to_save = None

    try:
        models_ = product_soup.find('div', id='selectMoremodelsWrapper').find_all('li')
        print('ЕСТЬ МОДЕЛИ')
    except:
        parse_models = False
        print('НЕТУ МОДЕЛЕЙ')

    if parse_models:
        for model in models_:
            models_article = model.get('data-url').split('/')[-2]
            if models_article not in models_articles_list:
                models_articles_list.append(models_article)
        if len(models_articles_list) != 0:
            models_to_save = '#'.join(models_articles_list)
            print('Количество моделей продукта %i' % len(models_articles_list))'''

    return redirect(reverse('home'))


