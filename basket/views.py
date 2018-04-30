from django.shortcuts import render, HttpResponse
from django.views.generic import DetailView
from shop.views import MainInfo
from django.http import JsonResponse
from ikea_parser.create_identificator import create_identificator
from ikea_parser.models import Product
from .models import *

# Create your views here.

class Basket(MainInfo, DetailView):
    template_name = 'basket/basket.html'


def add_to_basket(request):
    if request.method == 'POST' and request.is_ajax():
        product_article = request.POST['product_article']
        count = request.POST['count']

        session_key = request.session.session_key
        try:
            existed_order = Order.objects.get(session_key=session_key)
        except Order.DoesNotExist:
            existed_order = Order.objects.create(session_key=session_key, unique_identificator=create_identificator(16), status='новый')
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
