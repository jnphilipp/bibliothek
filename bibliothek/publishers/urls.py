# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^publisher/$', views.ListView.as_view(), name='publisher_list'),
    url(r'^publisher/(?P<slug>[\w-]+)/$', views.DetailView.as_view(), name='publisher_detail'),
]
