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

from django.conf.urls import url
from .views.book import DetailView as BookDetailView, ListView
from .views.edition import DetailView as EditionDetailView


urlpatterns = [
    url(r'^book/$', ListView.as_view(), name='book_list'),
    url(r'^book/(?P<slug>[\w-]+)/$', BookDetailView.as_view(),
        name='book_detail'),
    url(r'^book/(?P<slug>[\w-]+)/edition/(?P<pk>[0-9]+)/$',
        EditionDetailView.as_view(), name='edition_detail'),
]
