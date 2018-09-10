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

from books.models import Edition
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from utils import lookahead, stdout


def all(book=None):
    fields = [_('Id'), _('Title'), _('Binding'), _('ISBN'),
              _('Publishing date')]

    editions = Edition.objects.all()
    if book is not None:
        editions = editions.filter(book=book)
    _list([[edition.id, edition.get_title(), edition.binding, edition.isbn,
            edition.publishing_date] for edition in editions], fields,
          positions=[.05, .35, .55, .75])
    return editions


def by_shelf(shelf, book=None):
    fields = [_('Id'), _('Title'), _('Binding'), _('ISBN'),
              _('Publishing date')]

    editions = Edition.objects.all()
    if book is not None:
        editions = editions.filter(book=book)
    if shelf == 'read':
        editions = editions.filter(reads__isnull=False)
    elif shelf == 'unread':
        editions = editions.filter(
            Q(reads__isnull=True) | Q(reads__finished__isnull=True)
        )
    editions = editions.distinct()
    _list([[edition.id, edition.get_title(), edition.binding, edition.isbn,
            edition.publishing_date] for edition in editions], fields,
          positions=[.05, .35, .55, .75])
    return editions


def by_term(term, book=None):
    fields = [_('Id'), _('Title'), _('Binding'), _('ISBN'),
              _('Publishing date')]

    editions = Edition.objects.all()
    if book is not None:
        editions = editions.filter(book=book)

    editions = editions.filter(Q(pk=term if term.isdigit() else None) |
                               Q(alternate_title__icontains=term) |
                               Q(isbn__icontains=term) |
                               Q(book__title__icontains=term))
    _list([[edition.id, edition.get_title(), edition.binding, edition.isbn,
            edition.publishing_date] for edition in editions], fields,
          positions=[.05, .35, .55, .75])
    return editions


def _list(editions, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for book, has_next in lookahead(editions):
        stdout.p(book, positions=positions, after='_' if has_next else '=')
