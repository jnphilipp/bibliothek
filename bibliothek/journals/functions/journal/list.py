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

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from journals.models import Journal
from utils import lookahead, stdout


def all():
    journals = Journal.objects.all()
    _list([[journal.id, journal.name,
            journal.papers.count()] for journal in journals],
          [_('Id'), _('Name'), _('#Papers')], positions=[.5, .9, 1.])
    return journals


def by_term(term):
    journals = Journal.objects.filter(
        Q(pk=term if term.isdigit() else None) | Q(name__icontains=term)
    )
    _list([[journal.id, journal.name,
            journal.papers.count()] for journal in journals],
          [_('Id'), _('Name'), _('#Papers')], positions=[.5, .9, 1.])
    return journals


def _list(journals, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for journal, has_next in lookahead(journals):
        stdout.p(journal, positions=positions, after='_' if has_next else '=')
