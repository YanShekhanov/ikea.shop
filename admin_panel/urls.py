from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^orders/$', DisplayOrders.as_view(), name='display_orders'),
]