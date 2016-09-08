# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^series/$', views.ListView.as_view(), name='series_list'),
    url(r'^series/(?P<slug>[\w-]+)/$', views.DetailView.as_view(), name='series_detail'),
]
