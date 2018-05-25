from django.views.generic import TemplateView, ListView, FormView, DetailView
from django.views.generic.edit import UpdateView
from basket.models import *
from ikea_parser.models import Category, SubCategory, SubSubCategory
from django.shortcuts import render, redirect, reverse, Http404
from django.http import JsonResponse
from .forms import ChangeStatusForm, AdminAuthForm, DownloadProductForm, ChangePaymentForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login

LOGIN_URL = '/admin_panel/auth'

class AdminAuth(FormView):
    template_name = 'admin_panel/login.html'
    form_class = AdminAuthForm
    success_url = '/admin_panel/orders/'
    context_object_name = 'form'

    def get(self, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return redirect(self.success_url)
            else:
                return redirect(reverse('catalogue'))
        else:
            return super(AdminAuth, self).get(*args, **kwargs)

    #login form
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username', '')
        password = self.request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            if self.request.user.is_superuser:
                return super(AdminAuth, self).post(*args, **kwargs)
            else:
                return redirect(reverse('catalogue'))

class UpdateProduct(UpdateView):
    model = Product
    fields = '__all__'
    template_name = 'admin_panel/edit_product.html'
    slug_url_kwarg = 'article_number'
    slug_field = 'article_number'

    def get_success_url(self):
        url = reverse('productDetail', args=[self.kwargs.get('article_number')])
        return url

class DisplayOrders(ListView):
    template_name = 'admin_panel/orders.html'
    context_object_name = 'orders'
    model = Order

    def get(self, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return super(DisplayOrders, self).get(*args, **kwargs)
            else:
                return redirect(reverse('catalogue'))
        else:
            return redirect(reverse('adminAuth'))

    def get_queryset(self):
        self.queryset = self.model._default_manager.exclude(status=0).order_by('-first_registration')
        return self.queryset

    def get_context_data(self, **kwargs):
        orders_info = []
        orders_delivery = []
        orders_payment = []
        self.objects_list = self.get_queryset()
        for order in self.objects_list:
            orders_info.append(OrderRegistration.objects.get(order=order))
            orders_delivery.append(DeliveryMethod.objects.get(order=order))
            orders_payment.append(PaymentMethod.objects.get(order=order))
        context = super(DisplayOrders, self).get_context_data(**kwargs)
        context['orders_info'] = orders_info
        context['orders_delivery'] = orders_delivery
        context['orders_payment'] = orders_payment
        context['change_order_status_form'] = ChangeStatusForm
        context['change_payment_method_form'] = ChangePaymentForm
        context['article_number_form'] = DownloadProductForm
        return context

class SearchOrder(ListView):
    template_name = 'admin_panel/orders.html'
    model = Order
    context_objects_name = 'orders'
    options = ['date', 'unique_identificator']

    def get(self, *args, **kwargs):
        option = self.kwargs.get('option')
        value = self.kwargs.get('value')
        if option not in self.options:
            raise Http404('Option not found')
        else:
            if option == 'unique_identificator':
                self.objects_list = Order.objects.filter(unique_identificator=value)
                print(self.objects_list)
                return super(SearchOrder, self).get(*args, **kwargs)

from ikea_parser.models import ProductImage
from basket.models import ProductInOrder, Order
def order_detail(request):
    response_dict = {}
    if request.method == 'POST' and request.is_ajax():
        products_list = []
        order = Order.objects.get(unique_identificator=request.POST['unique_identificator'])
        products_in_order = ProductInOrder.objects.filter(order=order).order_by('-created')
        for product in products_in_order:
            image = ProductImage.objects.filter(product=product.product, size=250).first()
            print(image.image.url)
            one_product_dict = {
                'title':product.product.title,
                'article_number':product.product.article_number,
                'article_number_with_dot':product.product.with_dot(),
                'price_per_one':product.product.price,
                'price':product.price,
                'count':product.count,
                'image':image.image.url,
            }
            products_list.append(one_product_dict)
        response_dict = {'success':True, 'unique_identificator':order.unique_identificator, 'products':products_list}
        return JsonResponse(response_dict)
    else:
        response_dict['methodError'] = 'Bad request'
        raise Http404(response_dict)

def change_order_status(request):
    response_dict = {}
    if request.method == "POST" and request.is_ajax():
        status = request.POST['status']
        order_unique_identificator = request.POST['unique_identificator']
        try:
            existed_order = Order.objects.get(unique_identificator=order_unique_identificator)
            existed_order.status = status
            existed_order.save()
            response_dict['success'] = {'successMessage': 'Успiшно змiнено деталi замовлення'}
            return JsonResponse(response_dict)
        except:
            response_dict['existError'] = 'Order does not exist'
    else:
        response_dict['requestError'] = 'Bad request'
    return JsonResponse(response_dict)

def change_payment_method(request):
    response_dict = {}
    if request.method == 'POST' and request.is_ajax():
        try:
            order_payment = PaymentMethod.objects.get(order=Order.objects.get(unique_identificator=request.POST['unique_identificator']))
            order_payment.payment_method = request.POST['payment_method']
            order_payment.amount = request.POST['amount']
            order_payment.save()
            response_dict['success'] = {'successMessage': 'Успiшно змiнено деталi замовлення'}
            return JsonResponse(response_dict)
        except OrderRegistration.DoesNotExist or Order.DoesNotExist:
            response_dict['existError'] = 'Order does not exist'
            return JsonResponse(response_dict)
    else:
        response_dict['requestError'] = 'Bad request'
        return JsonResponse(response_dict)

#удаление заказа
def delete_order(request):
    response_dict = {}
    if request.method == 'POST' and request.is_ajax():
        unique_identificator = request.POST['unique_identificator']
        try:
            order = Order.objects.get(unique_identificator=unique_identificator)
            order.delete()
            response_dict['successMessage'] = 'Замовлення було видалено'
        except Order.DoesNotExist:
            response_dict['existError'] = 'Замовлення не знайдено'
        return JsonResponse(response_dict)
    else:
        response_dict['requestError'] = 'Bad request'

#удаление продукта
def delete_product(request):
    response_dict = {}
    if request.method == "POST" and request.is_ajax():
        article_number = request.POST['article_number']
        try:
            product = Product.objects.get(article_number=article_number)
            response_dict['successMessage'] = u'Артикул видалено'
            response_dict['article_number'] = product.with_dot()
            response_dict['redirect_url'] = reverse('getOneCategoryProducts', args=[product.subcategory.all()[0].unique_identificator])
            product.delete()
        except Product.DoesNotExist:
            response_dict['existError'] = u'Артикул не знайдено'
        return JsonResponse(response_dict)
    else:
        response_dict['requestError'] = u'Bad request'
        return JsonResponse(response_dict)

class DownloadProduct(FormView, TemplateView):
    form_class = DownloadProductForm
    template_name = 'admin_panel/download_product.html'

    def get(self, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return super(DownloadProduct, self).get(*args, **kwargs)
            else:
                return redirect(reverse('catalogue'))
        else:
            return redirect(reverse('catalogue'))

    def post(self, *args, **kwargs):
        if self.request.is_ajax():
            response_dict = {}
            categories_dict = {}
            have_sub_subcategory = self.request.POST['have_sub_subcategory']
            if have_sub_subcategory == True:
                categories_dict['sub_subcategory_id'] = self.request.POST['sub_subcategory_id']
            article_number = self.request.POST['article_number']
            categories_dict['subcategory_id'] = self.request.POST['subcategory_id']
            function_response = parse_with_article_number(article_number, **categories_dict)
            return JsonResponse(function_response)

    def get_context_data(self):
        context = super(DownloadProduct, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['subcategories'] = SubCategory.objects.all()
        context['sub_subcategories'] = SubSubCategory.objects.all()
        return context


from ikea_parser.ikea_parser import DOMAIN
from googletrans import Translator
import requests
from bs4 import BeautifulSoup
from shop.models import Coef
from ikea_parser.ikea_parser import parse_one_product_information_
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
def parse_with_article_number(article_number, **categories_dict):
    response_dict = {}
    try:
        existed_product = Product.objects.get(article_number=article_number, is_parsed=True)
        response_dict['duplicateError'] = 'Вказаний артикул вже наявний в БД'
        response_dict['url'] = reverse('productDetail', args=[article_number])
        return response_dict
    except Product.DoesNotExist:
        translator = Translator()
        # available in Lublin
        detail_page = 'https://www.ikea.com/pl/pl/catalog/products/%s/' % article_number
        product_available_url = 'http://www.ikea.com/pl/pl/iows/catalog/availability/%s/' % (
            article_number)

        product_request = requests.get(product_available_url).text
        product_page = BeautifulSoup(product_request, 'xml')
        product_detail = BeautifulSoup(requests.get(detail_page).text, 'lxml')
        try:
            available = product_page.find('localStore', buCode='311').find('availableStock').get_text()
        except AttributeError:
            available = 0

        #парсинг основной информации
        product_price = product_detail.find('span', class_='packagePrice').text.strip().split()[:2]
        product_title = product_detail.find('span', class_='productName').text.strip()
        product_description = product_detail.find('span', class_='productType').text.strip()
        if product_price[1] == 'PLN':
            product_price = product_price[0]
        product_price = ''.join(product_price)
        for symbol in product_price:
            if symbol == ' ':
                product_price = ''.join(product_price.split(' '))
        for symbol in product_price:
            if symbol == ',':
                product_price = '.'.join(product_price.split(','))
        product_price = int(round(float(product_price) * Coef.objects.all().first().coef))
        print(product_price)

        product_unit = product_detail.find('span', class_='unit')  # /шт.
        if product_unit is not None:
            product_unit = product_unit.text.strip()
        else:
            product_unit = ''

        if categories_dict.get('sub_subcategory_id') is not None:
            created_product = Product.objects.create(title=product_title, article_number=article_number, description=product_description, price=product_price,
                                                     url_ikea=detail_page)
            created_product.subcategory.add(SubCategory.objects.get(id=categories_dict.get('subcategory_id')))
            created_product.sub_subcategory.add(SubSubCategory.objects.get(id=categories_dict.get('sub_subcategory_id')))
        else:
            created_product = Product.objects.create(title=product_title, article_number=article_number, description=product_description,
                                                    price=product_price,
                                                    url_ikea=detail_page)
            created_product.subcategory.add(SubCategory.objects.get(id=categories_dict.get('subcategory_id')))

        #парсинг всей информации и картинок
        options = Options()
        options.add_argument("--headless")
        options.add_argument("window-size=1024,768")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(chrome_options=options)
        parse_one_product_information_(created_product, driver)
        driver.close()

        response_dict = {
            'article_number':article_number,
            'title':product_title,
            'description':product_description,
            'price':product_price
        }
        return response_dict

    # create Product
    # если продукт находится в подкатегории
    '''if subcategory_status:
        created_product = Product.objects.create(article_number=product_article, title=product_title,
                                                 description=product_description, price=float(product_price),
                                                 url_ikea=product_url, available=available,
                                                 unique_identificator=create_identificator(8))
        created_product.subcategory.add(foreign_key_query)
        iter_category_products_number += 1
    # если продукт находится в под подкатегории
    elif sub_subcategory_status:
        subcategory = foreign_key_query.subcategory
        created_product = Product.objects.create(article_number=product_article, title=product_title,
                                                 description=product_description, price=float(product_price),
                                                 url_ikea=product_url, available=available,
                                                 unique_identificator=create_identificator(8))
        created_product.subcategory.add(subcategory)
        created_product.sub_subcategory.add(foreign_key_query)
        iter_category_products_number += 1

    # создание словаря одного продукта
    one_product_dict = {
        'title': str(product_title.encode('utf-8')),
        'article_number': product_article,
        'product_availability': available,
        'product_price': product_price,
        'product_description': str(product_description.encode('utf-8')),
        'product_url': product_url,
        'subcategory': subcategory_status,
        'sub_subcategory': sub_subcategory_status,
        'subcategory_title': str(foreign_key_query.title.encode('utf-8')),
        'subcategory_url': foreign_key_query.url_ikea,
    }'''

