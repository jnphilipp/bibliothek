# -*- coding: utf-8 -*-

import re

from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from shelves.models import Read
from utils import lookahead, stdout


def add(edition, started=None, finished=None):
    read = Read.objects.create(started=started, finished=finished, content_object=edition)
    stdout.p([_('Successfully added read "%(id)s" to edition "%(edition)s".') % {'id':read.id, 'edition':str(edition)}], positions=[1.])
    _print(read)
    return read


def delete(edition, read_id):
    try:
        read = edition.reads.get(pk=read_id)
        _print(read)
        read.delete()
        stdout.p([_('Successfully deleted read.')], positions=[1.])
    except Read.DoesNotExist:
        stdout.p([_('A read with id "%(id)s" for this edition does not exist.') % {'id':read_id}], after='=', positions=[1.])


def edit(edition, read_id, field, value):
    assert field in ['started', 'finished']

    try:
        read = edition.reads.get(pk=read_id)
        if field == 'started':
            read.started = value
        elif field == 'finished':
            read.finished = value
        read.save()
        stdout.p([_('Successfully edited read "%(id)s".') % {'id':read.id}], positions=[1.])
        _print(read)
    except Read.DoesNotExist:
        stdout.p([_('A read with id "%(id)s" for this edition does not exist.') % {'id':read_id}], after='=', positions=[1.])


def _print(read):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), read.id], positions=positions)
    stdout.p([_('Date started'), read.started], positions=positions)
    stdout.p([_('Date finished'), read.finished], after='=', positions=positions)
