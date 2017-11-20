# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
#
# This file is part of bibliothek.
#
# bibliothek is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# bibliothek is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with bibliothek.  If not, see <http://www.gnu.org/licenses/>.

"""bibliothek URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views import static
from . import views

admin.site.site_header = 'Bibliothek administration'


urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),

    url(r'^books/', include('books.urls', 'books')),
    url(r'^journals/', include('journals.urls', 'journals')),
    url(r'^genres/', include('genres.urls', 'genres')),
    url(r'^magazines/', include('magazines.urls', 'magazines')),
    url(r'^papers/', include('papers.urls', 'papers')),
    url(r'^persons/', include('persons.urls', 'persons')),
    url(r'^publishers/', include('publishers.urls', 'publishers')),
    url(r'^series/', include('series.urls', 'series')),

    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += [url(r'^media/(?P<path>.*)$', static.serve,
                        {'document_root': settings.MEDIA_ROOT})]
