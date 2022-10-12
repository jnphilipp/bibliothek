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
"""Publishers Django app views."""

from django.db.models import Count
from django.db.models.functions import Lower
from django.views import generic
from publishers.models import Publisher


class ListView(generic.ListView):
    """Genre list view."""

    model = Publisher

    def get_context_data(self, **kwargs):
        """Get context data."""
        context = super(ListView, self).get_context_data(**kwargs)
        context["o"] = "name"
        if self.request.GET.get("o"):
            context["o"] = self.request.GET.get("o")
        return context

    def get_queryset(self):
        """Get Django query set."""
        o = self.request.GET.get("o") if self.request.GET.get("o") else "name"
        o = o.replace("name", "iname")
        publishers = Publisher.objects.annotate(
            ce=Count("editions"), iname=Lower("name")
        ).order_by(o)
        return publishers


class DetailView(generic.DetailView):
    """Genre detail view."""

    model = Publisher

    def get_context_data(self, **kwargs):
        """Get context data."""
        context = super(DetailView, self).get_context_data(**kwargs)
        context["eo"] = "book__title"
        if self.request.GET.get("eo"):
            context["eo"] = self.request.GET.get("eo")
        context["editions"] = self.object.editions.order_by(context["eo"])

        context["po"] = "title"
        if self.request.GET.get("po"):
            context["po"] = self.request.GET.get("po")
        context["papers"] = self.object.papers.order_by(context["po"])
        return context
