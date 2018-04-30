from django.shortcuts import render
from django.views.generic import DetailView
from shop.views import MainInfo
from django.http import JsonResponse

# Create your views here.

class Basket(MainInfo, DetailView):
    template_name = 'basket/basket.html'


def add_to_basket(request):
    if request.method == 'POST' and request.is_ajax():
        product_article = request.POST['product_article']
        count = request.POST['count']
        print(product_article, count)
        response_dict = {
            'added':True,
            'product_article':product_article,
        }
        return JsonResponse(response_dict)
