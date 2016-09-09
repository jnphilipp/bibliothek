# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^genre/$', views.ListView.as_view(), name='genre_list'),
    url(r'^genre/(?P<slug>[\w-]+)/$', views.DetailView.as_view(), name='genre_detail'),
]
