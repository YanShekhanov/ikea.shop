from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^orders/$', DisplayOrders.as_view(), name='display_orders'),
    url(r'^order_detail/$', order_detail, name='order_detail'), #ajax
]