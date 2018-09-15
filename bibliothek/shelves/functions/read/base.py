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

from django.utils.translation import ugettext_lazy as _
from shelves.models import Read
from utils import stdout


def create(obj, started=None, finished=None):
    read = Read.objects.create(started=started, finished=finished,
                               content_object=obj)

    info(read)
    msg = _('Successfully added read "%(id)s".')
    stdout.p([msg % {'id': read.id}])
    return read


def delete(read):
    read.delete()
    stdout.p([_('Successfully deleted read.')])


def edit(read, field, value):
    assert field in ['started', 'finished']

    if field == 'started':
        read.started = value
    elif field == 'finished':
        read.finished = value
    read.save()
    stdout.p([_('Successfully edited read "%(id)s".') % {'id': read.id}])


def info(read):
    positions = [.33]
    stdout.p([_('Id'), read.id], positions=positions)
    stdout.p([_('Obj'), read.content_object], positions=positions)
    stdout.p([_('Date started'), read.started], positions=positions)
    stdout.p([_('Date finished'), read.finished], positions=positions)
