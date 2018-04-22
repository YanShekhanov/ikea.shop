from django.conf.urls import url
from django.urls import path
from .views import *

urlpatterns = [

    url(r'^$', HomePage.as_view(), name='home'),
    url(r'^delete_images/$', delete_images, name='delete_images'), #удаление изображений
    url(r'^delete_categories/$', delete_categories, name='delete_categories'), #удаление продуктов
    url(r'^delete_products/$', delete_products, name='delete_products'), #удаление продуктов
    url(r'^parse_categories/$', parse_categories, name='parse_categories'), #парсинг категорий, подкатегорий
    url(r'^parse_products_articles/$', parse_products_articles, name='parse_products_articles'), #парсинг артикулов
    url(r'^parse_products_information/$', parse_products_information, name='parse_products_information'), #парсинг изображений и информации артикула
    url(r'^parse_rooms/$', parse_rooms, name='parse_rooms'),
    url(r'^parse_examples/$', parse_rooms_examples, name='parse_rooms_examples'),

    url(r'^test/$', test, name='test'),
]
