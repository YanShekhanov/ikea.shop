from django.views.generic import TemplateView, ListView
from basket.models import *
from django.shortcut import render, redirect, reverse, JsonResponse

class DisplayOrders(ListView):
    template_name = 'admin_panel/orders.html'
    context_object_name = 'orders'
    model = Order

    def get_queryset(self):
        self.queryset = self.model._default_manager.exclude(status=0)
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
        return context

def order_detail(request):
    if request.method == 'POST' and request.is_ajax():
        print(request.POST['unique_identificator'])
        return JsonResponse({'data':True})