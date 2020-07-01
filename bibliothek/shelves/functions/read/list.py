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
from shelves.models import Read


def all():
    return Read.objects.all()


def by_term(term):
    return Read.objects.annotate(
        jv=Concat('papers__journal__name', Value(' '), 'papers__volume'),
        ni=Concat('issues__magazine__name', Value(' '), 'issues__issue')). \
        filter(Q(pk=term if term.isdigit() else None) |
               Q(editions__alternate_title__icontains=term) |
               Q(editions__isbn__icontains=term) | Q(jv__icontains=term) |
               Q(ni__iregex=term.replace(' ', '.*?')) |
               Q(papers__title__icontains=term) |
               Q(editions__book__title__icontains=term)).distinct()
