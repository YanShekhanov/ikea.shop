from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^add_to_basket/$', add_to_basket, name='add_to_basket'),
    url(r'^$', ShowBasket.as_view(), name='show_basket'),
    url(r'^change_product/$', change_product, name='change_product'),
    url(r'^delete_product_from_basket/$', delete_product_from_basket, name='delete_product_from_basket'),
    url(r'^refresh_basket/$', refresh_basket, name='refresh_basket'),
    url(r'^order_registration/$', OrderReg.as_view(), name='order_registration'),
    url(r'^order_registration/success/$', order_registration, name='ajax_order_registration'),
]