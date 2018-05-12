from django.conf.urls import url
from django.urls import path
from .views import *

urlpatterns = [
    url(r'^$', MainInfo.as_view(), name='catalogue'),

    url(r'^downloadOneProductInformation/$', DownloadOneProductInformation.as_view(), name='downloadOneProductInformation'),
    url(r'^product_detail/product=(?P<article_number>\w+)/$', ProductDetail.as_view(), name='productDetail'),
    url(r'^query=(?P<category_identificator>\w+)/$', GetOneCategoryProducts.as_view(), name='getOneCategoryProducts'),
    url(r'rooms/room_place=(?P<unique_identificator>\w+)/$', RoomPlaceDetail.as_view(), name='roomPlaceDetail'),
    url(r'rooms/example=(?P<unqiue_identificator>)', ExampleDetail.as_view(), name='exampleDetail'),
    #url(r'rooms/room_detail/room=(?P<unique_identificator>\w+)/$', RoomExampleDetail.as_view(), name='roomExampleDetail'),

    #ajax
    url(r'^getAllProductImages/$', get_all_product_images, name='get_all_product_images'),
    url(r'^getSortQuery/$', get_sort_query, name='getSortQuery'),
    url(r'^search/$', search, name='search'),
    url(r'^checkAvailability/$', check_availability, name='checkAvailability'),
]