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

from books.models import Edition
from django.db.models import Q, Value
from django.db.models.functions import Concat
from persons.models import Person


def all(book=None):
    editions = Edition.objects.all()
    if book is not None:
        editions = editions.filter(book=book)
    return editions


def by_shelf(shelf, book=None):
    editions = Edition.objects.all()
    if book is not None:
        editions = editions.filter(book=book)
    if shelf == 'read':
        editions = editions.filter(reads__isnull=False)
    elif shelf == 'unread':
        editions = editions.filter(Q(reads__isnull=True) |
                                   Q(reads__finished__isnull=True))
    return editions.distinct()


def by_term(term, book=None, has_file=None):
    persons = Person.objects.annotate(name=Concat('first_name', Value(' '),
                                                  'last_name')). \
        filter(Q(pk=term if term.isdigit() else None) |
               Q(name__icontains=term))

    editions = Edition.objects.all()
    if book is not None:
        editions = editions.filter(book=book)
    if has_file is not None:
        editions = editions.filter(files__isnull=not has_file)
    return editions.filter(Q(pk=term if term.isdigit() else None) |
                           Q(alternate_title__icontains=term) |
                           Q(isbn__icontains=term) | Q(persons__in=persons) |
                           Q(book__authors__in=persons) |
                           Q(book__series__name__icontains=term) |
                           Q(book__title__icontains=term)).distinct()
