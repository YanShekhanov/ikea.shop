from django.shortcuts import render, HttpResponse, redirect, reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView
from shop.views import MainInfo
from django.http import JsonResponse, Http404
from ikea_parser.create_identificator import create_num_identificator
from ikea_parser.models import Product, ProductImage
from .models import *
from ikea_parser.create_identificator import create_num_identificator, create_identificator

# Create your views here.

#показать корзину
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

#страница с формой для регистрации заказа
from .forms import OrderRegistrationForm, DeliveryMethodForm, PaymentMethodForm
class OrderReg(MainInfo, FormView):
    form_class = OrderRegistrationForm
    template_name = 'basket/order_registration.html'
    context_object_name = 'form'

    def get_context_data(self, **kwargs):
        context = super(OrderReg, self).get_context_data(**kwargs)
        try:
            context['order'] = Order.objects.get(session_key=self.request.session.session_key)
            context['products'] = ProductInOrder.objects.filter(order=context.get('order'))
            context['DeliveryMethodForm'] = DeliveryMethodForm
            context['PaymentMethodForm'] = PaymentMethodForm
        except Order.DoesNotExist:
            raise Http404()
        return context

#ajax регистрация информации по доставке
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
        try:
            order = Order.objects.get(session_key=request.session.session_key)
            order_regis = OrderRegistration.objects.create(order=order, name=name, sorname=sorname, second_name=second_name,
                                                           phone=phone, email=email, attentions=attentions)
            delivery = DeliveryMethod.objects.create(order=order, delivery_method=delivery_method, city=city, adres=adres, department_number=department_number)
            payment = PaymentMethod.objects.create(order=order, payment_method=payment_method, amount=amount)

            order.status = 1
            order.session_key = create_identificator(16)
            order.save()
            response_dict = {
                'success':True,
                'success_message':u'Ваш заказ успешно создан и принят в обработку.',
                'order_info':{
                    'unique_identificator':order.unique_identificator,
                    'date':order.updated.strftime('yyyy.mm.dd H:m'),
                    'email':email,
                }
            }
        except:
            response_dict = {
                'success':False,
                'error_message':u'Что-то пошло не так, попробуйте еще раз'
            }
        return JsonResponse(response_dict)
    else:
        raise Http404()

from shop.views import availability
#ajax изменения кол-ва продукта в корзине
def change_product(request):
    response_dict = {}
    if request.method == 'POST' and request.is_ajax():
        count = request.POST['count']
        product_article_number = request.POST['product_article_number']

        #проверяем на доступность продукт
        #check_availability
        product_availability = availability(product_article_number)
        if product_availability.get('availability'):
            if int(count) > int(product_availability.get('availability')):
                response_dict['availabilityError'] = {'message': u'Введенное количество привышает доступное', 'availability':product_availability.get('availability')}
            else:
                product_in_order = ProductInOrder.objects.get(product=Product.objects.get(article_number=product_article_number),
                                                              order=Order.objects.get(session_key=request.session.session_key))
                product_in_order.count = int(count)
                product_in_order.save()
                response_dict['success'] = {'message': u'Количество изменено'}
        else:
            response_dict['serverError'] = {'message': u'Повторите попытку позже или обратитесь к администратору'}
    else:
        response_dict['methodError'] = "Bad request"
    return JsonResponse(response_dict)

#ajax удаление продукта с корзины
def delete_product_from_basket(request):
    if request.method == 'POST' and request.is_ajax():
        product_article_number = request.POST['product_article_number']
        product_to_delete = ProductInOrder.objects.get(product=Product.objects.get(article_number=product_article_number),
                                                       order=Order.objects.get(session_key=request.session.session_key))
        product_to_delete.delete()
        response_dict = {
            'deleted': True,
        }
        return JsonResponse(response_dict)

from shop.views import availability
#ajax добавление продкта в корзину
def add_to_basket(request):
    response_dict = {}
    if request.method == 'POST' and request.is_ajax():
        product_article = request.POST['product_article']
        count = int(request.POST['count'])

        product_availability = availability(product_article)
        if product_availability.get('successMessage'):
            return JsonResponse(response_dict={'successMessage': 'К сожалению данный продукт временно недоступен'})
        if product_availability.get('availability'):
            response_dict['availability'] = product_availability['availability']
            pass

        if count > product_availability.get('availability'):
            response_dict['countError'] = {'message':'Введенное количество привышает доступное', 'availability': product_availability['availability']}
            return JsonResponse(response_dict)

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

        response_dict['added'] = True
        response_dict['product_article'] = created_in_basket.product.with_dot()
        response_dict['product_title'] = created_in_basket.product.title
        response_dict['count'] = count
        '''response_dict = {
            'added':True,
            'product_article':created_in_basket.product.article_number,
            'product_title':created_in_basket.product.title,
            'count':count
        }'''
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
                'product_title':product_in_order.product.title,
                'article_number':product_in_order.product.article_number,
                'article_number_with_dot':product_in_order.product.with_dot(),
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

def refresh_basket_price(request):
    response_dict = {}
    if request.method == 'POST' and request.is_ajax():
        order = Order.objects.get(session_key=request.session.session_key)
        response_dict['order'] = {'order_price':str(int(order.order_price)), 'product_count':len(list(ProductInOrder.objects.filter(order=order)))}
        return JsonResponse(response_dict)
    else:
        response_dict['methodError'] = 'Bad request'
        raise Http404(response_dict)
