from django.shortcuts import render, HttpResponse
from django.views.generic import DetailView, ListView
from shop.views import MainInfo
from django.http import JsonResponse
from ikea_parser.create_identificator import create_identificator
from ikea_parser.models import Product, ProductImage
from .models import *

# Create your views here.

class ShowBasket(MainInfo, ListView):
    template_name = 'basket/basket.html'
    model = ProductInOrder
    context_object_name = 'products'
    paginate_by = 100

    def get_queryset(self):
        self.queryset = ProductInOrder.objects.filter(order=Order.objects.get(session_key=self.request.session.session_key))
        return self.queryset

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super(ShowBasket, self).get_context_data(**kwargs)
        if len(self.object_list) == 0:
            context['ExistError'] = True
        if not context.get('ExistError'):
            images_list = []
            for product in self.queryset:
                image = ProductImage.objects.filter(product=product.product, size=250).first()
                images_list.append(image)
            context['images'] = images_list
            context['order'] = Order.objects.get(session_key=self.request.session.session_key)
        return context

def change_product(request):
    if request.method == 'POST' and request.is_ajax():
        pass

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
            existed_order = Order.objects.create(session_key=session_key, unique_identificator=create_identificator(16))
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
