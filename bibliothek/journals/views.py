# -*- coding: utf-8 -*-
# Copyright (C) 2016-2021 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Journals Django app views."""

from django.db.models import Count
from django.db.models.query import QuerySet
from django.views import generic
from journals.models import Journal
from typing import Dict


class ListView(generic.ListView):
    """Journl list view."""

    model = Journal

    def get_context_data(self, **kwargs) -> Dict:
        """Get context data."""
        context = super(ListView, self).get_context_data(**kwargs)
        context["o"] = "name"
        if self.request.GET.get("o"):
            context["o"] = self.request.GET.get("o")
        return context

    def get_queryset(self) -> QuerySet[Journal]:
        """Get django query set."""
        o = self.request.GET.get("o") if self.request.GET.get("o") else "name"
        return Journal.objects.annotate(cp=Count("papers")).order_by(o)


class DetailView(generic.DetailView):
    """Journal detail view."""

    model = Journal

    def get_context_data(self, **kwargs) -> Dict:
        """Get context data."""
        context = super(DetailView, self).get_context_data(**kwargs)
        context["o"] = "title"
        if self.request.GET.get("o"):
            context["o"] = self.request.GET.get("o")
        context["papers"] = self.object.papers.order_by(context["o"])
        return context
