from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^auth/$', AdminAuth.as_view(), name='adminAuth'),
    url(r'^orders/$', DisplayOrders.as_view(), name='display_orders'),
    url(r'^edit_product/product=(?P<article_number>\w+)/$', UpdateProduct.as_view(), name='edit_product'),
    url(r'^order_detail/$', order_detail, name='order_detail'), #ajax
    url(r'^change_order_status/$', change_order_status, name='change_order_status'), #ajax
    url(r'^change_payment_method/$', change_payment_method, name='change_payment_method'), #ajax
    url(r'^delete_product/$', delete_product, name='delete_product'),
    url(r'^download_product/$', DownloadProduct.as_view(), name='download_product')#ajax
]