from django.shortcuts import render, HttpResponse, redirect, reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView
from shop.views import MainInfo
from django.http import JsonResponse
from ikea_parser.create_identificator import create_num_identificator
from ikea_parser.models import Product, ProductImage
from .models import *
from ikea_parser.create_identificator import create_num_identificator, create_identificator

# Create your views here.

class ShowBasket(MainInfo, ListView):
    template_name = 'basket/basket.html'
    model = ProductInOrder
    context_object_name = 'products'

    def get_queryset(self):
        self.product_error_404 = False
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        try:
            order = Order.objects.get(session_key=self.request.session.session_key)
            print('existed order')
            self.queryset = list(ProductInOrder.objects.filter(order=order).order_by('-created'))
            if not self.queryset:
                self.product_error_404 = True
        except Order.DoesNotExist:
            self.order = Order.objects.create(session_key=self.request.session.session_key, unique_identificator=create_num_identificator(8))
            self.product_error_404 = True
        return self.queryset

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super(ShowBasket, self).get_context_data(**kwargs)
        if self.product_error_404:
            context['ExistError'] = True
        else:
            images_list = []
            for product in self.queryset:
                image = ProductImage.objects.filter(product=product.product, size=250).first()
                images_list.append(image)
            context['images'] = images_list
            context['order'] = Order.objects.get(session_key=self.request.session.session_key)
        return context

from .forms import OrderRegistrationForm, DeliveryMethodForm, PaymentMethodForm
class OrderRegis(MainInfo, FormView):
    form_class = OrderRegistrationForm
    template_name = 'basket/order_registration.html'
    context_object_name = 'form'

    def get_context_data(self, **kwargs):
        context = super(OrderRegis, self).get_context_data(**kwargs)
        context['order'] = Order.objects.get(session_key=self.request.session.session_key)
        context['products'] = ProductInOrder.objects.filter(order=context.get('order'))
        context['DeliveryMethodForm'] = DeliveryMethodForm
        context['PaymentMethodForm'] = PaymentMethodForm
        return context

from .models import *
def order_registration(request):
    if request.method == "POST" and request.is_ajax():
        request_dict = request.POST
        name = request_dict['name']
        sorname = request_dict['sorname']
        second_name = request_dict['second_name']
        phone = request_dict['phone']
        email = request_dict['email']
        attentions = request_dict['attentions']
        city = request_dict['city']
        delivery_method = request_dict['delivery_method']
        adres = request_dict['adres']
        department_number = request_dict['department_number']
        payment_method = request_dict['payment_method']
        amount = request_dict['amount']

        order = Order.objects.get(session_key=request.session.session_key)
        order_regis = OrderRegistration.objects.get(order=order)
        order_regis.name = name
        order_regis.sorname = sorname
        order_regis.second_name = second_name
        order_regis.phone = phone
        order_regis.email = email
        if attentions != '':
            order_regis.attentions = attentions
        order_regis.save()

        delivery = DeliveryMethod.objects.get(order=order)
        delivery.delivery_method = delivery_method
        delivery.city = city
        delivery.adres = adres
        delivery.department_number = department_number
        delivery.save()

        payment = PaymentMethod.objects.get(order=order)
        payment.payment_method = payment_method
        payment.amount = amount
        payment.save()

        order.status = 1
        order.session_key = create_identificator(16)
        order.save()
        return redirect(reverse('order_registration'))

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


#ajax обновление корзины
def refresh_basket(request):
    if request.method == 'GET' and request.is_ajax():
        session_key = request.session.session_key
        order = Order.objects.get(session_key=session_key)
        products_in_order = ProductInOrder.objects.filter(order=order).order_by('-created')
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
            'order_price':order.order_price,
        }
        return JsonResponse(response_dict)
