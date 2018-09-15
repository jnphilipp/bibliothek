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

from django.db.models import Q
from utils import stdout

from . import list as edition_list


def by_term(term, book=None):
    editions = edition_list.by_term(term, book)

    if editions.count() == 0:
        stdout.p(['No edition found.'], after='=')
        print('\n')
        return None
    elif editions.count() > 1:
        if term.isdigit():
            editions = editions.filter(pk=term)
        else:
            editions = editions.filter(Q(alternate_title=term) | Q(isbn=term) |
                                       Q(book__title=term))
        if editions.count() != 1:
            stdout.p(['More than one edition found.'], after='=')
            print('\n')
            return None
    print('\n')
    return editions[0]
