from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^auth/$', AdminAuth.as_view(), name='adminAuth'),
    url(r'^check_auth/$', check_auth, name='check_auth'),
    url(r'^orders/$', DisplayOrders.as_view(), name='display_orders'),
    url(r'^order_detail/$', order_detail, name='order_detail'), #ajax
    url(r'^change_order_status/$', change_order_status, name='change_order_status'), #ajax
]