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

from django.db.models import Count
from django.views import generic
from magazines.models import Magazine


class ListView(generic.ListView):
    model = Magazine

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context["o"] = "name"
        if self.request.GET.get("o"):
            context["o"] = self.request.GET.get("o")
        return context

    def get_queryset(self):
        o = self.request.GET.get("o") if self.request.GET.get("o") else "name"
        return Magazine.objects.annotate(ci=Count("issues")).order_by(o)


class DetailView(generic.DetailView):
    model = Magazine

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["o"] = "-publishing_date"
        if self.request.GET.get("o"):
            context["o"] = self.request.GET.get("o")
        context["issues"] = self.object.issues.order_by(context["o"])
        return context
