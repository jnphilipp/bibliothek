# -*- coding: utf-8 -*-
"""bibliothek URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views import static
from . import views

admin.site.site_header = 'Bibliothek administration'


urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),

    url(r'^books/', include('books.urls')),
    url(r'^journals/', include('journals.urls')),
    url(r'^magazines/', include('magazines.urls')),
    url(r'^papers/', include('papers.urls')),
    url(r'^persons/', include('persons.urls')),
    url(r'^publishers/', include('publishers.urls')),
    url(r'^series/', include('series.urls')),

    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += [url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT})]
