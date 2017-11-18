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
from django.utils.translation import ugettext_lazy as _
from series.models import Series
from utils import lookahead, stdout


def all():
    series = Series.objects.all()
    _list([[series.id, series.name] for series in series],
          [_('Id'), _('Name')], positions=[.05, 1.])
    return series


def by_term(term):
    series = Series.objects.filter(
        Q(pk=term if term.isdigit() else None) | Q(name__icontains=term)
    )
    _list([[series.id, series.name] for series in series],
          [_('Id'), _('Name')], positions=[.05, 1.])
    return series


def _list(series, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for series, has_next in lookahead(series):
        stdout.p(series, positions=positions, after='_' if has_next else '=')
