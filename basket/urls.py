from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^add_to_basket/$', add_to_basket, name='add_to_basket'),
    url(r'^$', ShowBasket.as_view(), name='show_basket'),
]