# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import book, edition


urlpatterns = [
    url(r'^book/$', book.ListView.as_view(), name='book_list'),
    url(r'^book/(?P<slug>[\w-]+)/$', book.DetailView.as_view(), name='book_detail'),
    url(r'^book/(?P<slug>[\w-]+)/edition/(?P<pk>[0-9]+)/$', edition.DetailView.as_view(), name='edition_detail'),
]
