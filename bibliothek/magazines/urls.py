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
from .views.issue import DetailView as IssueDetailView
from .views.magazine import DetailView as MagazineDetailView, ListView


urlpatterns = [
    url(r'^magazine/$', ListView.as_view(), name='magazine_list'),
    url(r'^magazine/(?P<slug>[\w-]+)/$', MagazineDetailView.as_view(),
        name='magazine_detail'),
    url(r'^magazine/(?P<slug>[\w-]+)/issue/(?P<pk>[0-9]+)/$',
        IssueDetailView.as_view(), name='issue_detail'),
]
