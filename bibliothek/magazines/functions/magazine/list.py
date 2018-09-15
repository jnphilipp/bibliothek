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
from magazines.models import Magazine
from utils import lookahead, stdout


def all():
    magazines = Magazine.objects.all()
    _list([[magazine.id, magazine.name,
            magazine.issues.count()] for magazine in magazines],
          [_('Id'), _('Name'), _('#Issues')], positions=[.05, .8])
    return magazines


def by_term(term):
    magazines = Magazine.objects.filter(
        Q(pk=term if term.isdigit() else None) | Q(name__icontains=term)
    )
    _list([[magazine.id, magazine.name,
            magazine.issues.count()] for magazine in magazines],
          [_('Id'), _('Name'), _('#Issues')], positions=[.05, .8])
    return magazines


def _list(magazines, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for magazine, has_next in lookahead(magazines):
        stdout.p(magazine, positions=positions, after='_' if has_next else '=')
