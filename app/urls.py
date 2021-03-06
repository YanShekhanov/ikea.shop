"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, static
from django.conf import settings
from django.urls import include
from shop.views import MainInfo


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('shop.urls'), name='shop'),
    url(r'^parse/', include('ikea_parser.urls'), name='parse'),
    url(r'^basket/', include('basket.urls'), name='basket'),
    url(r'^admin_panel/', include('admin_panel.urls'), name='admin-panel'),
] #+ static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  #+ static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.views.static import serve
from django.conf import settings
urlpatterns += [url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
                            url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT})]
