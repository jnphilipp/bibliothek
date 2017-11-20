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

import re

from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from shelves.models import Read
from utils import lookahead, stdout


def add(edition, started=None, finished=None):
    read = Read.objects.create(started=started, finished=finished,
                               content_object=edition)
    msg = _('Successfully added read "%(id)s" to edition "%(edition)s".')
    stdout.p([msg % {'id': read.id, 'edition': str(edition)}], positions=[1.])
    _print(read)
    return read


def delete(edition, read_id):
    try:
        read = edition.reads.get(pk=read_id)
        _print(read)
        read.delete()
        stdout.p([_('Successfully deleted read.')], positions=[1.])
    except Read.DoesNotExist:
        msg = _('A read with id "%(id)s" for this edition does not exist.')
        stdout.p([msg % {'id':read_id}], after='=', positions=[1.])


def edit(edition, read_id, field, value):
    assert field in ['started', 'finished']

    try:
        read = edition.reads.get(pk=read_id)
        if field == 'started':
            read.started = value
        elif field == 'finished':
            read.finished = value
        read.save()
        stdout.p([_('Successfully edited read "%(id)s".') % {'id': read.id}],
                 positions=[1.])
        _print(read)
    except Read.DoesNotExist:
        msg = _('A read with id "%(id)s" for this edition does not exist.')
        stdout.p([msg % {'id':read_id}], after='=', positions=[1.])


def _print(read):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), read.id], positions=positions)
    stdout.p([_('Date started'), read.started], positions=positions)
    stdout.p([_('Date finished'), read.finished], after='=',
             positions=positions)
