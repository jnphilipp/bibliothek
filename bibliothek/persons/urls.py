# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^person/$', views.persons, name='persons'),
    url(r'^person/(?P<slug>[\w-]+)/$', views.person, name='person'),
]
