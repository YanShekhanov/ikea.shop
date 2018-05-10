from django.views.generic import TemplateView, ListView, FormView
from basket.models import *
from django.shortcuts import render, redirect, reverse, Http404
from django.http import JsonResponse
from .forms import ChangeStatusForm

class DisplayOrders(ListView):
    template_name = 'admin_panel/orders.html'
    context_object_name = 'orders'
    model = Order

    def get_queryset(self):
        self.queryset = self.model._default_manager.exclude(status=0).order_by('-created')
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
        return context

    def post(self, *args, **kwargs):
        form = self.get_form(self.form_class)
        if form.is_valid():
            print(form.cleaned_data['status', ''])
            return redirect(reverse('home'))

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
    pass