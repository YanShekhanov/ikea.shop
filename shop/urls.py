from django.conf.urls import url
from django.urls import path
from .views import *

urlpatterns = [
    url(r'^$', MainInfo.as_view(), name='catalogue'),

    url(r'^downloadOneProductInformation/$', DownloadOneProductInformation.as_view(), name='downloadOneProductInformation'),
    url(r'^product_detail/product=(?P<article_number>\w+)/$', ProductDetail.as_view(), name='productDetail'),
    url(r'^query=(?P<category_identificator>\w+)/$', GetOneCategoryProducts.as_view(), name='getOneCategoryProducts'),

    #ajax
    url(r'^getAllProductImages/$', get_all_product_images, name='get_all_product_images'),
]