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

from . import list as paper_list


def by_term(term):
    papers = paper_list.by_term(term)

    if papers.count() == 0:
        stdout.p([_('No paper found.')], after='=')
        return None
    elif papers.count() > 1:
        papers = papers.annotate(
            jv=Concat('journal__name', Value(' '), 'volume',
                      output_field=TextField()))
        if term.isdigit():
            papers = papers.filter(pk=term)
        else:
            papers = papers.filter(Q(title=term) | Q(jv=term))
        if papers.count() != 1:
            stdout.p(['More than one paper found.'], after='=')
            return None
    print('\n')
    return papers[0]
