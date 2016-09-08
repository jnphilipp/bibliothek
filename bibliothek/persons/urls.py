# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^person/$', views.ListView.as_view(), name='person_list'),
    url(r'^person/(?P<slug>[\w-]+)/$', views.DetailView.as_view(), name='person_detail'),
]
