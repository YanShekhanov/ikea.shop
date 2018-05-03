from django.shortcuts import render, HttpResponse
from django.views.generic import DetailView, ListView
from shop.views import MainInfo
from django.http import JsonResponse
from ikea_parser.create_identificator import create_num_identificator
from ikea_parser.models import Product, ProductImage
from .models import *
from ikea_parser.create_identificator import create_num_identificator

# Create your views here.

class ShowBasket(MainInfo, ListView):
    template_name = 'basket/basket.html'
    model = ProductInOrder
    context_object_name = 'products'

    def get_queryset(self):
        self.product_error_404 = False
        try:
            self.order = Order.objects.get(session_key=self.request.session.session_key)
            try:
                self.queryset = ProductInOrder.objects.filter(order=self.order)
                self.queryset = self.queryset.order_by('created')
            except ProductInOrder.DoesNotExist:
                self.product_error_404 = True
        except Order.DoesNotExist:
            self.order = Order.objects.create(session_key=self.request.session.session_key, unique_identificator=create_num_identificator(8))
            self.product_error_404 = True
        return self.queryset

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super(ShowBasket, self).get_context_data(**kwargs)
        if self.product_error_404 == True:
            context['ExistsError'] = True
        else:
            images_list = []
            for product in self.queryset:
                image = ProductImage.objects.filter(product=product.product, size=250).first()
                images_list.append(image)
            context['images'] = images_list
            context['order'] = Order.objects.get(session_key=self.request.session.session_key)
        return context

def change_product(request):
    if request.method == 'POST' and request.is_ajax():
        count = request.POST['count']
        order_unique_identificator = request.POST['order_unique_identificator']
        product_unique_identificator = request.POST['product_unique_identificator']
        product_in_order = ProductInOrder.objects.get(product=Product.objects.get(unique_identificator=product_unique_identificator),
                                                      order=Order.objects.get(unique_identificator=order_unique_identificator))
        product_in_order.count = count
        product_in_order.save()
        return JsonResponse({'success_message':'okey'})

def delete_product_from_basket(request):
    if request.method == 'POST' and request.is_ajax():
        order_unique_identificator = request.POST['order_identificator']
        product_unique_identificator = request.POST['product_identificator']
        product_to_delete = ProductInOrder.objects.get(product=Product.objects.get(unique_identificator=product_unique_identificator),
                                                       order=Order.objects.get(unique_identificator=order_unique_identificator))
        product_to_delete.delete()
        response_dict = {
            'deleted': True,
        }
        return JsonResponse(response_dict)

def order_detail(request):
    pass


def add_to_basket(request):
    if request.method == 'POST' and request.is_ajax():
        product_article = request.POST['product_article']
        count = int(request.POST['count'])

        if not request.session.exists(request.session.session_key):
            request.session.create()
        session_key = request.session.session_key

        try:
            existed_order = Order.objects.get(session_key=session_key)
        except Order.DoesNotExist:
            existed_order = Order.objects.create(session_key=session_key, unique_identificator=create_num_identificator(8))
        try:
            existed_product = Product.objects.get(article_number=product_article)
            try:
                created_in_basket = ProductInOrder.objects.get(order=existed_order, product=existed_product)
                created_in_basket.count += count
                created_in_basket.save()
            except ProductInOrder.DoesNotExist:
                created_in_basket = ProductInOrder.objects.create(order=existed_order, product=existed_product, count=count)
        except Product.DoesNotExist:
            return HttpResponse(status=404)

        print(product_article, count)
        response_dict = {
            'added':True,
            'product_article':product_article,
            'count':count
        }
        return JsonResponse(response_dict)

def refresh_basket(request):
    if request.method == 'GET' and request.is_ajax():
        session_key = request.session.session_key
        order = Order.objects.get(session_key=session_key)
        products_in_order = ProductInOrder.objects.filter(order=order).order_by('created')
        products_list = []
        for product_in_order in products_in_order:
            one_product_dict = {
                'image_url':ProductImage.objects.filter(product=product_in_order.product, size=250).first().image.url,
                'product_unique_identificator':product_in_order.product.unique_identificator,
                'product_title':product_in_order.product.title,
                'article_number':product_in_order.product.article_number,
                'count':product_in_order.count,
                'price_per_one':product_in_order.price_per_one,
                'price':product_in_order.price,
            }
            products_list.append(one_product_dict)
        response_dict = {
            'products':products_list,
            'order_unique_identificator':order.unique_identificator,
        }
        return JsonResponse(response_dict)