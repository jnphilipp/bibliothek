# -*- coding: utf-8 -*-

import re

from datetime import datetime
from papers.models import Paper
from shelves.models import Read
from utils import lookahead, stdout


def add(paper, started=None, finished=None):
    read = Read.objects.create(started=started, finished=finished, content_object=paper)
    stdout.p(['Successfully added read "%s" to paper "%s".' % (read.id, paper.title)], positions=[1.])
    _print(read)
    return read


def delete(paper, id):
    try:
        read = paper.reads.get(pk=id)
        _print(read)
        read.delete()
        stdout.p(['Successfully deleted read.'], positions=[1.])
    except Read.DoesNotExist:
        stdout.p(['A read with id "%s" for this paper does not exist.' % id], after='=', positions=[1.])


def edit(paper, id, field, value):
    assert field in ['started', 'finished']

    try:
        read = paper.reads.get(pk=id)
        if field == 'started':
            read.started = value
        elif field == 'finished':
            read.finished = value
        read.save()
        stdout.p(['Successfully edited read "%s".' % read.id], positions=[1.])
        _print(read)
        return read
    except Read.DoesNotExist:
        stdout.p(['A read with id "%s" for this paper does not exist.' % id], after='=', positions=[1.])
        return None


def _print(read):
    positions=[.33, 1.]
    stdout.p(['Field', 'Value'], positions=positions, after='=')
    stdout.p(['Id', read.id], positions=positions)
    stdout.p(['Date started', read.started], positions=positions)
    stdout.p(['Date finished', read.finished], after='=', positions=positions)
