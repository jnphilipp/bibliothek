# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import issue, magazine


urlpatterns = [
    url(r'^magazine/$', magazine.magazines, name='magazines'),
    url(r'^magazine/(?P<slug>[\w-]+)/$', magazine.magazine, name='magazine'),

    url(r'^magazine/(?P<magazine_slug>[\w-]+)/issue/$', issue.issues, name='issues'),
    url(r'^magazine/(?P<magazine_slug>[\w-]+)/issue/(?P<issue_slug>[\w-]+)/$', issue.issue, name='issue'),
]
