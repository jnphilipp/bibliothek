# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2016-2022 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Magazines Django app urls."""

from django.urls import path
from .views.issue import DetailView as IssueDetailView
from .views.magazine import DetailView as MagazineDetailView, ListView


app_name = "magazines"
urlpatterns = [
    path("magazine/", ListView.as_view(), name="magazine_list"),
    path("magazine/<slug:slug>/", MagazineDetailView.as_view(), name="magazine_detail"),
    path(
        "magazine/<slug:slug>/issue/<int:pk>/",
        IssueDetailView.as_view(),
        name="issue_detail",
    ),
]
