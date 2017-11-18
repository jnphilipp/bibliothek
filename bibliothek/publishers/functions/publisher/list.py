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
from publishers.models import Publisher
from utils import lookahead, stdout


def all():
    publishers = Publisher.objects.all()
    _list([[publisher.id, publisher.name] for publisher in publishers],
          [_('Id'), _('Name')], positions=[.05, 1.])
    return publishers


def by_term(term):
    publishers = Publisher.objects.filter(
        Q(pk=term if term.isdigit() else None) | Q(name__icontains=term)
    )
    _list([[publisher.id, publisher.name] for publisher in publishers],
          [_('Id'), _('Name')], positions=[.05, 1.])
    return publishers


def _list(publishers, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for publisher, has_next in lookahead(publishers):
        stdout.p(publisher, positions=positions,
                 after='_' if has_next else '=')
