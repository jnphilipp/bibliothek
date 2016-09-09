# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^journal/$', views.ListView.as_view(), name='journal_list'),
    url(r'^journal/(?P<slug>[\w-]+)/$', views.DetailView.as_view(), name='journal_detail'),
]
