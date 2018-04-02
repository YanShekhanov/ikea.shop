from django.shortcuts import render
from ikea_parser.models import *
from .form import *
from django.views.generic import ListView, FormView, DetailView, TemplateView, View
from django.shortcuts import redirect, reverse
from django.contrib.messages import error
from django.shortcuts import Http404
from django.http import JsonResponse

from ikea_parser.parseWithArticleNumber import parseOneProductInformationWithArticleNumber

# Create your views here.

class MainInfo(TemplateView):
    template_name = 'shop_template.html'

    def get_context_data(self, **kwargs):
        context = super(MainInfo, self).get_context_data(**kwargs)
        context['Categories'] = Category.objects.exclude(title='Panele słoneczne')
        context['SubCategories'] = SubCategory.objects.all()
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

    def get_queryset(self):
        try:
            query = SubCategory.objects.get(unique_identificator=self.kwargs.get('category_identificator'))
        except SubCategory.DoesNotExist:
            try:
                query = SubSubCategory.objects.get(unique_identificator=self.kwargs.get('category_identificator'))
            except SubSubCategory.DoesNotExist:
                return Http404
        self.queryset = query
        return self.queryset

    def get_context_data(self, **kwargs):
        self.object = self.get_queryset()
        context = super(GetOneCategoryProducts, self).get_context_data(**kwargs)
        context['products'] = Product.objects.filter(subcategory=self.object)
        products_images = []
        for product in context.get('products'):
            first_image = ProductImage.objects.filter(product=product)
            if len(first_image) > 1: #если больше одной картинке к одному артикулу, тогда отдаем только первую
                products_images.append(first_image[0])
            elif len(first_image) == 1: #если только одна картинка к артикулу, отдаем ее
                products_images.append(first_image)
        context['productsImages'] = products_images
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
            context['productsImages'] = ProductImage.objects.filter(product=self.object, size=500)
        except ProductImage.DoesNotExist:
            pass

        #Дополняющие продукты
        complementary_products_list = self.object.complementary_products.split('#')
        if complementary_products_list == []:
            complementary_products_list = None #если None, то не отображается блок "Дополняющие продукты" на странице

        complementary_products_query = []
        complementary_products_images_query = []
        for complementary_product in complementary_products_list:
            try:
                #дополняющие товары
                complementary_one_product_query = Product.objects.get(article_number=complementary_product)
                complementary_products_query.append(complementary_one_product_query)
                #изображения дополняющих товаров
                try:
                    complementary_one_product_images_query = ProductImage.objects.filter(product=Product.objects.get(article_number=complementary_product))
                    for image in complementary_one_product_images_query:
                        complementary_products_images_query.append(image)
                except ProductImage.DoesNotExist:
                    print('Не найдены изображения к артикулу %s' % complementary_product)
            except Product.DoesNotExist:
                pass
        context['complementaryProducts'] = complementary_products_query
        context['complementaryProductsImages'] = complementary_products_images_query
        context['Categories'] = Category.objects.exclude(title='Panele słoneczne')
        context['SubCategories'] = SubCategory.objects.all()

        #Цвета
        color_options_list = self.object.color_options.split('#')
        context['colorOptions'] = color_options_list

        #Модели
        additionals_models_list = self.object.additional_models.split('#')
        context['models'] = additionals_models_list
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


def get_sort_query(request):
    from django.core import serializers
    sort_by_dict = {
        'increase':'price',
        'decline':'-price',
        'from_A_to_Z':'title',
        'from_Z_to_A':'-title'
    }
    if request.method == 'POST' and request.is_ajax():
        sort_by_from_post = request.POST['sort_by']
        unique_identificator = request.POST['unique_identificator']
        query = None

        try:
            sort_by = sort_by_dict.get(sort_by_from_post)
        except:
            return Http404

        try:
            query = SubCategory.objects.get(unique_identificator=unique_identificator)
        except SubCategory.DoesNotExist:
            try:
                query = SubSubCategory.objects.get(unique_identificator=unique_identificator)
            except SubSubCategory.DoesNotExist:
                return redirect(reverse('home'))
        response_json_dict = {
            'data': serializers.serialize('json', Product.objects.filter(subcategory=query).order_by(sort_by))
        }
        print(type(response_json_dict))
        return JsonResponse(response_json_dict, safe=False)



#AJAX LOAD ALL IMAGES FOR ARTICLE
def get_all_product_images(request):
    unique_identificator = request.POST['unique_identificator']
    all_images = ProductImage.objects.filter(product=Product.objects.get(unique_identificator=unique_identificator), size=500)
    all_images_list = []
    for image in all_images:
        all_images_list.append(image.image.url)
    json_response = {'images':all_images_list}
    return JsonResponse(data=json_response)






