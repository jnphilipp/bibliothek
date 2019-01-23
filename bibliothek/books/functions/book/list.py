#!/usr/bin/env python3
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

from books.models import Book
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _
from persons.models import Person


def all():
    return Book.objects.all()


def by_shelf(shelf):
    books = Book.objects.all()
    if shelf == 'read':
        books = books.filter(editions__reads__isnull=False)
    elif shelf == 'unread':
        books = books.filter(editions__reads__isnull=True)
    return books.distinct()


def by_term(term):
    persons = Person.objects.annotate(name=Concat('first_name', Value(' '),
                                                  'last_name')). \
        filter(Q(pk=term if term.isdigit() else None) |
               Q(name__icontains=term))

    return Book.objects.filter(Q(pk=term if term.isdigit() else None) |
                               Q(title__icontains=term) |
                               Q(authors__in=persons) |
                               Q(series__name__icontains=term)).distinct()
