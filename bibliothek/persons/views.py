# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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

from django.db.models import Case, CharField, Count, When
from django.views import generic
from persons.models import Person


class ListView(generic.ListView):
    model = Person

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['o'] = 'name'
        if self.request.GET.get('o'):
            context['o'] = self.request.GET.get('o')
        return context

    def get_queryset(self):
        o = self.request.GET.get('o') if self.request.GET.get('o') else 'name'
        persons = Person.objects.annotate(cb=Count('books'),
                                          cp=Count('papers'))
        if o.endswith('name'):
            persons = persons.order_by('name')
        else:
            persons = persons.order_by(o)
        return persons


class DetailView(generic.DetailView):
    model = Person

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['bo'] = 'title'
        context['eo'] = 'title'
        context['po'] = 'title'

        if self.request.GET.get('bo'):
            context['bo'] = self.request.GET.get('bo')
        if self.request.GET.get('eo'):
            context['eo'] = self.request.GET.get('eo')
        if self.request.GET.get('po'):
            context['po'] = self.request.GET.get('po')

        context['books'] = self.object.books.annotate(ce=Count('editions')). \
            order_by(context['bo'])
        context['editions'] = self.object.editions.annotate(
            title=Case(
                When(alternate_title__isnull=False, then='alternate_title'),
                default='book__title',
                output_field=CharField(),
            )).all().order_by(context['eo'])
        context['papers'] = self.object.papers.order_by(context['po'])
        return context
