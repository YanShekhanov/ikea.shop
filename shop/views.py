from django.shortcuts import render
from ikea_parser.models import *
from .form import *
from django.views.generic import ListView, FormView, DetailView, TemplateView, View
from django.shortcuts import redirect, reverse
from django.contrib.messages import error
from django.shortcuts import Http404
from django.http import JsonResponse

from ikea_parser.parseWithArticleNumber import parseOneProductInformationWithArticleNumber
from django.contrib.auth.decorators import login_required

# Create your views here.

def redirect_to_home(request):
    home_page = 'catalogue'
    return redirect(reverse(home_page))

from basket.models import Order, ProductInOrder
from ikea_parser.create_identificator import create_num_identificator
class MainInfo(TemplateView):
    template_name = 'shop_template.html'

    def get_context_data(self, **kwargs):
        context = super(MainInfo, self).get_context_data(**kwargs)
        context['Categories'] = Category.objects.exclude(not_display=True).order_by('-created')
        context['SubCategories'] = SubCategory.objects.exclude(not_display=True).order_by('-created')
        context['SubSubCategories'] = SubSubCategory.objects.exclude(not_display=True).order_by('-created')

        #user
        user = self.request.user
        if user.is_authenticated:
            context['username'] = user.username
            if user.is_superuser:
                context['is_superuser'] = True

        #rooms
        rooms = Room.objects.exclude(not_display=True)
        rooms_places = []
        for room in rooms:
            room_places = RoomPlace.objects.filter(room=room)
            for room_place in room_places:
                rooms_places.append(room_place)
        context['Rooms'] = rooms
        context['RoomsPlaces'] = rooms_places

        #basket
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        try:
            order = Order.objects.get(session_key=self.request.session.session_key)
        except Order.DoesNotExist:
            order = Order.objects.create(session_key=self.request.session.session_key, unique_identificator=create_num_identificator(8))
        context['order_price'] = order.order_price
        context['product_count'] = len(list(ProductInOrder.objects.filter(order=order)))

        from django.utils.timezone import datetime
        print(datetime.today())
        return context

class Home(MainInfo, ListView):
    template_name = 'shop/home_page.html'
    context_object_name = 'examples'

    def get_queryset(self):
        random_room_nmb = 3
        rooms = Room.objects.exclude(not_display=True)
        room_length = len(rooms)
        room_list = []  # рандомные комнаты
        for _ in range(random_room_nmb):
            random_room = Room.objects.exclude(not_display=True)[random.randint(0, (len(Room.objects.exclude(not_display=True)) - 1))]
            room_list.append(random_room)

        room_place_list = []
        for room in room_list:
            room_place = RoomPlace.objects.filter(room=room)[
                random.randint(0, (len(RoomPlace.objects.filter(room=room)) - 1))]
            room_place_list.append(room_place)

        room_example_list = []
        for room_place in room_place_list:
            room_example = RoomExample.objects.filter(room_place=room_place)[
                random.randint(0, (len(RoomExample.objects.filter(room_place=room_place)) - 1))]
            room_example_list.append(room_example)

        self.queryset = room_example_list
        return self.queryset

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        image_list = []
        for room_example in self.object_list:
            image = ExampleImage.objects.get(example=room_example, is_presentation=False)
            image_list.append(image)
        context = super(Home, self).get_context_data(**kwargs)
        context['exampleImages'] = image_list
        context['rooms'] = Room.objects.exclude(not_display=True)
        context['rooms_places'] = RoomPlace.objects.exclude(not_display=True)
        return context

import random
#главная страница
class Catalogue(MainInfo, ListView):
    template_name = 'shop/catalogue.html'
    model = Product
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super(Catalogue, self).get_context_data(**kwargs)
        context['productsImages'] = ProductImage.objects.all()
        return context

#открытие категории с артикулами
class GetOneCategoryProducts(MainInfo, DetailView):
    template_name = 'shop/catalogue.html'
    context_object_name = 'category'
    slug_url_kwarg = 'category_identificator'
    is_subcategory = False
    is_sub_subcategory = False

    def get_queryset(self):
        try:
            query = SubCategory.objects.get(unique_identificator=self.kwargs.get('category_identificator'))
            self.is_subcategory = True
        except SubCategory.DoesNotExist:
            try:
                query = SubSubCategory.objects.get(unique_identificator=self.kwargs.get('category_identificator'))
                self.is_sub_subcategory = True
            except SubSubCategory.DoesNotExist:
                return Http404
        self.queryset = query
        return self.queryset

    def get_context_data(self, **kwargs):
        self.object = self.get_queryset()
        context = super(GetOneCategoryProducts, self).get_context_data(**kwargs)
        if self.is_subcategory:
            if self.object.have_sub_subcategory:
                sub_subcategories = SubSubCategory.objects.filter(subcategory=self.object)
                context['subSubCategories'] = sub_subcategories
                context['displayCategories'] = True
                return context
            else:
                context['displayProducts'] = True
                context['is_filtered'] = True
            context['category_path'] = self.object.category
            context['subcategory_path'] = self.object
            context['is_subcategory'] = True
        if self.is_sub_subcategory:
            context['is_sub_subcategory'] = True
            context['category_path'] = self.object.subcategory.category
            context['subcategory_path'] = self.object.subcategory
            context['sub_subcategory_path'] = self.object
            context['displayProducts'] = True
            context['is_filtered'] = True
        return context

#страница одного товара
class ProductDetail(MainInfo, DetailView, TemplateView):
    template_name = 'shop/productDetail.html'
    model = Product
    slug_url_kwarg = 'article_number'
    slug_field = 'article_number'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(ProductDetail, self).get_context_data(**kwargs)
        '''#path
        context['category_path'] = self.object.subcategory.all[0].category
        context['subcategory_path'] = self.object.subcategory
        context['sub_subcategory_path'] = self.object.sub_subcategory
        '''

        #Изображения
        try:
            context['productImages'] = ProductImage.objects.filter(product=self.object, size=500)
            context['productImageLarge'] = context.get('productImages').first()
        except ProductImage.DoesNotExist:
            pass

        complementary_images_list = [] # все дополняющие артикулы
        complementary_images = [] #все изображения к дополняющим артикулам

        #Цвета
        color_options_list = []
        if self.object.color_options is not None and self.object.color_options != '':
            color_options = self.object.color_options.split('#')
            for color in color_options:
                try:
                    color_query = Product.objects.get(article_number=color)
                    color_options_list.append(color_query)
                    complementary_images_list.append(color_query)
                except Product.DoesNotExist:
                    pass
            context['colorOptions'] = color_options_list

        #Размеры
        size_options_list = []
        if self.object.size_options is not None and self.object.size_options != '':
            size_options = self.object.size_options.split('#')
            for size in size_options:
                try:
                    size_query = Product.objects.get(article_number=size)
                    size_options_list.append(size_query)
                    complementary_images_list.append(size_query)
                except Product.DoesNotExist:
                    pass
            context['sizeOptions'] = size_options_list

        #Модели
        additional_models_list = []
        if self.object.additional_models is not None and self.object.additional_models != '':
            additionals_models = self.object.additional_models.split('#')
            for model in additionals_models:
                try:
                    model_query = Product.objects.get(article_number=model)
                    additional_models_list.append(model_query)
                    complementary_images_list.append(model_query)
                except Product.DoesNotExist:
                    pass
            context['modelOptions'] = additional_models_list

        #Дополняющие
        complementary_products_list = []
        complementary_products_images = []
        if self.object.complementary_products is not None and self.object.complementary_products != '':
            complementary_products = self.object.complementary_products.split('#')
            for product in complementary_products:
                try:
                    product = Product.objects.get(article_number=product)
                    complementary_products_list.append(product)
                    #изображения
                    image = ProductImage.objects.filter(product=product, size=250).first()
                    complementary_products_images.append(image)
                except Product.DoesNotExist:
                    pass
        else:
            complementary_products_list = None
        context['complementaryProducts'] = complementary_products_list
        context['complementaryProductsImages'] = complementary_products_images

        #изображения к дополняющим артикулам
        for product in complementary_images_list:
            try:
                image = ProductImage.objects.get(product=product, is_icon=True)
            except ProductImage.MultipleObjectsReturned:
                image = ProductImage.objects.filter(product=product, is_icon=True).first()
            except ProductImage.DoesNotExist:
                image = ProductImage.objects.filter(product=product, size=250).first()
            if image not in complementary_images:
                complementary_images.append(image)
        context['complementaryImages'] = complementary_images
        return context

#пересмотреть
class RoomPlaceDetail(MainInfo, DetailView):
    template_name = 'shop/room_place.html'
    model = RoomPlace
    context_object_name = 'room_place'
    slug_url_kwarg = 'unique_identificator'
    slug_field = 'unique_identificator'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        room_examples = RoomExample.objects.filter(room_place=self.object)
        images_list = []
        for room_example in room_examples:
            image = ExampleImage.objects.get(example=room_example, is_presentation=True)
            images_list.append(image)
        context = super(RoomPlaceDetail, self).get_context_data(**kwargs)
        context['roomExamples'] = room_examples
        context['examplesImages'] = images_list
        context['roomPlace'] = self.object
        return context

class ExampleDetail(MainInfo, DetailView):
    template_name = 'shop/example_detail.html'
    model = RoomExample
    context_object_name = 'room'
    slug_url_kwarg = 'unique_identificator'
    slug_field = 'unique_identificator'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        image = ExampleImage.objects.get(example=self.object, is_presentation=False)
        products = self.object.products.split('#')
        products_list = []
        for product in products:
            try:
                product = Product.objects.get(article_number=product)
                products_list.append(product)
            except Product.DoesNotExist:
                print(product)
        products_images = []
        for product in products_list:
            products_images.append(ProductImage.objects.filter(product=product, size=250).first())
        context = super(ExampleDetail, self).get_context_data(**kwargs)
        context['image'] = image
        context['products'] = products_list
        context['products_images'] = products_images
        return context

#!!!!!!!!!!!!!!!!!!!!!!
#парсинг артикула по номеру артикула
class DownloadOneProductInformation(FormView):
    template_name = 'shop/downloadOneProductInformation.html'
    form_class = DownloadOneProductInformationForm

    def get_success_url(self):
        success_url = redirect(reverse('productDetail', args=[self.article_number]))
        return success_url

    def form_valid(self, form):
        self.article_number = form.cleaned_data['article_number']
        function_response = parseOneProductInformationWithArticleNumber(self.article_number)
        if function_response == FileExistsError:
            error(self.request, 'Артикул не доступен в Люблине')
            return redirect(reverse('home'))
        return self.get_success_url()

#ajax сортировка
def get_sort_query(request):
    sort_by_dict = {
        'normal':'-created',
        'increase':'price',
        'decline':'-price',
        'from_A_to_Z':'title',
        'from_Z_to_A':'-title'
    }
    response_json_dict = {}
    if request.method == 'POST' and request.is_ajax():
        sort_by_from_post = request.POST['sort_by']
        unique_identificator = request.POST['unique_identificator']
        query = None
        try:
            sort_by = sort_by_dict.get(sort_by_from_post)
        except:
            return Http404

        from ikea_parser.json_serializer import product_to_json
        try:
            query = SubCategory.objects.get(unique_identificator=unique_identificator)
            response_json_dict['data'] = product_to_json(Product.objects.filter(subcategory=query).order_by(sort_by))
        except SubCategory.DoesNotExist:
            try:
                query = SubSubCategory.objects.get(unique_identificator=unique_identificator)
                response_json_dict['data'] = product_to_json(Product.objects.filter(sub_subcategory=query).order_by(sort_by))
            except SubSubCategory.DoesNotExist:
                return Http404
        return JsonResponse(response_json_dict)


#ajax поиск
from django.db.models import Q
def search(request):
    if request.method =='POST' and request.is_ajax():
        searched_text = request.POST['searched_text']

        verificate_text = searched_text.split('.')
        if len(verificate_text) == 3:
            searched_text = ''.join(verificate_text)
        products = Product.objects.filter(
            Q(article_number__icontains=searched_text) |
            Q(title__icontains=searched_text) |
            Q(description__icontains=searched_text)
        )
        products_list = []
        for product in products:
            one_product_dict = {}
            try:
                image = ProductImage.objects.get(product=product, is_icon=True)
                image_url = image.image.url
            except ProductImage.DoesNotExist:
                image_url = None
            one_product_dict['product_title'] = product.title
            one_product_dict['product_article_number'] = product.article_number
            one_product_dict['article_number_with_dot'] = product.with_dot()
            one_product_dict['product_price'] = product.price
            one_product_dict['product_image'] = image_url
            products_list.append(one_product_dict)

        return JsonResponse({'products':products_list})


#AJAX LOAD ALL IMAGES FOR ARTICLE
def get_all_product_images(request):
    identificator = request.POST['unique_identificator']
    product = Product.objects.get(unique_identificator=identificator)
    #more models
    if product.additional_models is not None:
        models_products = Product.objects.filter(article_number=product.additional_models.split('#'))

    #colors
    if product.color_options is not None:
        colors = Product.objects.filter(article_number=product.color_options.split('#'))

    all_images = ProductImage.objects.filter(product=product, size=2000)
    all_images_list = []
    for image in all_images:
        all_images_list.append(image.image.url)
    json_response = {
        'images':all_images_list,
        'productPrice':product.price,
        'productDescription':product.description,
        'productDimensions':product.dimensions,}
    return JsonResponse(data=json_response)

#по запросу POST
import requests
from bs4 import BeautifulSoup
#ajax проверка наличия
def check_availability(request):
    response_dict = {}
    if request.method == 'POST' and request.is_ajax():
        response_dict = availability(request.POST['article_number'])
        return JsonResponse(response_dict)

#через передавваемый аргумент
def availability(article_number):
    response_dict = {}
    url = 'http://www.ikea.com/pl/pl/iows/catalog/availability/%s/' % (article_number)
    request = requests.get(url).text
    product_soup = BeautifulSoup(request, 'xml')
    try:
        availability = product_soup.find('localStore', buCode='311').find('availableStock').text
        if int(availability) == 0:
            response_dict['successMessage'] = 'zero'#'К сожалению этот продукт не доступен'
        else:
            response_dict['availability'] = int(availability)
    except AttributeError:
        response_dict['errorMessage'] = 'Произошла ошибка, повторите позже'
    return response_dict

#удаление продукта
def delete_product(request):
    response_dict = {}
    if request.method == "POST" and request.is_ajax():
        article_number = request.POST['article_number']
        try:
            product = Product.objects.get(article_number=article_number)
            product.delete()
            response_dict['successMessage'] = u'Артикул видалено'
            response_dict['article_number'] = product.with_dot()
            response_dict['redirect_url'] = reverse('getOneCategoryProducts', args=[product.subcategory.all()[0].unique_identificator])
        except Product.DoesNotExist:
            response_dict['existError'] = u'Артикул не знайдено'
        return JsonResponse(response_dict)
    else:
        response_dict['requestError'] = u'Bad request'
        return JsonResponse(response_dict)







