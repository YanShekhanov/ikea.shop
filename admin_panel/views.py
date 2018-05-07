from django.views.generic import TemplateView, ListView
from basket.models import *

class DisplayOrders(ListView):
    template_name = 'admin_panel/orders.html'
    context_object_name = 'orders'
    model = Order

    def get_context_data(self, **kwargs):
        self.objects_list = self.get_queryset()
        return super(DisplayOrders, self).get_context_data(**kwargs)
