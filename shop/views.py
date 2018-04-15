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

class MainInfo(TemplateView):
    template_name = 'shop_template.html'

    def get_context_data(self, **kwargs):
        context = super(MainInfo, self).get_context_data(**kwargs)
        context['Categories'] = Category.objects.exclude(title='Panele słoneczne').order_by('created')
        context['SubCategories'] = SubCategory.objects.all().order_by('created')
        return context

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
                return context
        context['is_filtered'] = True

        #отображение списка следования
        if self.is_subcategory:
            context['is_subcategory'] = True
        else:
            context['is_sub_subcategory'] = True
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
        context = super().get_context_data(**kwargs)

        #Изображения
        try:
            context['productImages'] = ProductImage.objects.filter(product=self.object, size=500)
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
        if self.object.complementary_products is not None and self.object.complementary_products != '':
            complementary_products = self.object.complementary_products.split('#')
            for product in complementary_products:
                try:
                    product = Product.objects.get(article_number=product)
                    complementary_products_list.append(product)
                    complementary_images_list.append(product)
                except Product.DoesNotExist:
                    pass
            context['complementaryProducts'] = complementary_products_list

        #изображения к дополняющим артикулам
        for product in complementary_images_list:
            try:
                image = ProductImage.objects.get(product=product, is_icon=True)
                print(image.image)
            except ProductImage.DoesNotExist:
                image = ProductImage.objects.filter(product=product, size=250).first()
            if image not in complementary_images:
                complementary_images.append(image)
        context['complementaryImages'] = complementary_images
        return context

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

        from ikea_parser.json_serializer import json_serializer
        try:
            query = SubCategory.objects.get(unique_identificator=unique_identificator)
            response_json_dict['data'] = json_serializer(Product.objects.filter(subcategory=query).order_by(sort_by))
        except SubCategory.DoesNotExist:
            try:
                query = SubSubCategory.objects.get(unique_identificator=unique_identificator)
                response_json_dict['data'] = json_serializer(Product.objects.filter(sub_subcategory=query).order_by(sort_by))
            except SubSubCategory.DoesNotExist:
                return Http404

        return JsonResponse(response_json_dict)

#ajax поиск
from django.db.models import Q
def search(request):
    if request.method =='POST' and request.is_ajax():
        searched_text = request.POST['searched_text']
        products = Product.objects.filter(
            Q(article_number__icontains=searched_text) |
            Q(title__icontains=searched_text) |
            Q(description__icontains=searched_text)
        )
        from ikea_parser.json_serializer import json_serializer
        json_response_dict = json_serializer(products)
        return JsonResponse(data={'products': json_response_dict})


#AJAX LOAD ALL IMAGES FOR ARTICLE
def get_all_product_images(request):
    unique_identificator = request.POST['unique_identificator']
    all_images = ProductImage.objects.filter(product=Product.objects.get(unique_identificator=unique_identificator), size=500)
    all_images_list = []
    for image in all_images:
        all_images_list.append(image.image.url)
    json_response = {'images':all_images_list}
    return JsonResponse(data=json_response)

#ajax проверка наличия
def check_availability(request):
    response_dict = {}
    if request.method == 'POST' and request.is_ajax():
        url = 'http://www.ikea.com/pl/pl/iows/catalog/availability/%s/' % (request.POST['article_number'])
        import requests
        from bs4 import BeautifulSoup
        request = requests.get(url).text
        product_soup = BeautifulSoup(request, 'xml')
        try:
            availability = product_soup.find('localStore', buCode='311').find('availableStock').text
            if int(availability) == 0:
                response_dict['successMessage'] = 'К сожалению этот продукт не доступен'
            else:
                response_dict['availability'] = availability
        except AttributeError:
            response_dict['errorMessage'] = 'Произошла ошибка, повторите позже'
        return JsonResponse(response_dict)

#translate query
def translate_query(request):
    product = Product.objects.all().first()
    product_fields = product._meta.get_fields()
    for field in product_fields:
        if field.many_to_many:
            pass
        try:
            attr = getattr(product, field.name)
            print(field.name)
            print(attr)
        except AttributeError:
            pass
    return redirect(reverse('home'))






