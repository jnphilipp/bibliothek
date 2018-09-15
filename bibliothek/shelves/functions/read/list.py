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

from django.db.models import Q, TextField, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _
from shelves.models import Read
from utils import lookahead, stdout


def all():
    reads = Read.objects.all()
    _list([[read.id, read.content_object, read.started,
            read.finished] for read in reads],
          [_('Id'), _('Obj'), _('Date started'), _('Date finished')],
          positions=[.05, .7, .85])
    return reads


def by_term(term):
    reads = Read.objects.annotate(
        jv=Concat('papers__journal__name', Value(' '), 'papers__volume',
                  output_field=TextField()),
        ni=Concat('issues__magazine__name', Value(' '), 'issues__issue',
                  output_field=TextField())
    ).filter(
        Q(pk=term if term.isdigit() else None) |
        Q(editions__alternate_title__icontains=term) |
        Q(editions__isbn__icontains=term) |
        Q(editions__book__title__icontains=term) |
        Q(papers__title__icontains=term) | Q(jv__icontains=term) |
        Q(ni__icontains=term)
    )
    _list([[read.id, read.content_object, read.started,
            read.finished] for read in reads],
          [_('Id'), _('Obj'), _('Date started'), _('Date finished')],
          positions=[.05, .7, .85])
    return reads


def _list(reads, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for read, has_next in lookahead(reads):
        stdout.p(read, positions=positions, after='_' if has_next else '=')
