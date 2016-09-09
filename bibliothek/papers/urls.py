# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^paper/$', views.ListView.as_view(), name='paper_list'),
    url(r'^paper/(?P<slug>[\w-]+)/$', views.DetailView.as_view(), name='paper_detail'),
]
