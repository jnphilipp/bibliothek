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

from django.db.models import Q, Value
from django.db.models.functions import Concat
from papers.models import Paper
from persons.models import Person


def all():
    return Paper.objects.all()


def by_shelf(shelf):
    papers = Paper.objects.all()
    if shelf == 'read':
        papers = papers.filter(reads__isnull=False)
    elif shelf == 'unread':
        papers = papers.filter(reads__isnull=True)
    return papers.distinct()


def by_term(term, has_file=None):
    persons = Person.objects.filter(Q(pk=term if term.isdigit() else None) |
                                    Q(name__icontains=term))

    papers = Paper.objects.annotate(jv=Concat('journal__name', Value(' '),
                                              'volume')).all()
    if has_file is not None:
        papers = papers.filter(files__isnull=not has_file)
    return papers.filter(Q(pk=term if term.isdigit() else None) |
                         Q(title__icontains=term) | Q(authors__in=persons) |
                         Q(jv__icontains=term)).distinct()
