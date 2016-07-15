# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^journal/$', views.journals, name='journals'),
    url(r'^journal/(?P<slug>[\w-]+)/$', views.journal, name='journal'),
]
