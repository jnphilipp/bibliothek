# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import issue, magazine


urlpatterns = [
    url(r'^magazine/$', magazine.ListView.as_view(), name='magazine_list'),
    url(r'^magazine/(?P<slug>[\w-]+)/$', magazine.DetailView.as_view(), name='magazine_detail'),
    url(r'^magazine/(?P<slug>[\w-]+)/issue/(?P<pk>[0-9]+)/$', issue.DetailView.as_view(), name='issue_detail'),
]
