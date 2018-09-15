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
from utils import stdout

from . import list as read_list


def by_term(term):
    reads = read_list.by_term(term)

    if reads.count() == 0:
        stdout.p([_('No read found.')], after='=')
        print('\n')
        return None
    elif reads.count() > 1:
        if term.isdigit():
            reads = reads.filter(pk=term)
        else:
            reads = reads.annotate(
                jv=Concat('papers__journal__name', Value(' '),
                          'papers__volume', output_field=TextField()),
                ni=Concat('issues__magazine__name', Value(' '),
                          'issues__issue', output_field=TextField())
            ).filter(Q(editions__alternate_title=term) |
                     Q(editions__isbn=term) | Q(editions__book__title=term) |
                     Q(papers__title=term) | Q(jv=term) | Q(ni=term)
            )
        if reads.count() != 1:
            stdout.p([_('More than one read found.')], after='=')
            print('\n')
            return None
    print('\n')
    return reads[0]
