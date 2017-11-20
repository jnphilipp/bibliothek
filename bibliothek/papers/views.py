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

from django.db.models import Count
from django.views import generic
from papers.models import Paper


class ListView(generic.ListView):
    model = Paper

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['o'] = 'title'
        if self.request.GET.get('o'):
            context['o'] = self.request.GET.get('o')
        return context

    def get_queryset(self):
        o = self.request.GET.get('o') if self.request.GET.get('o') else 'title'
        return Paper.objects.order_by(o)


class DetailView(generic.DetailView):
    model = Paper
