# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^paper/$', views.papers, name='papers'),
    url(r'^paper/(?P<slug>[\w-]+)/$', views.paper, name='paper'),
]
