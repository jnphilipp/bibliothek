# -*- coding: utf-8 -*-

import re

from datetime import datetime
from shelves.models import Acquisition
from utils import lookahead, stdout


def add(issue, date=None, price=0.0):
    acquisition = Acquisition.objects.create(date=date, price=price, content_object=issue)
    stdout.p(['Successfully added acquisition "%s" to issue "%s" "%s".' % (acquisition.id, issue.magazine.name, issue.issue)], positions=[1.])
    _print(acquisition)


def delete(issue, id):
    try:
        acquisition = issue.acquisitions.get(pk=id)
        _print(acquisition)
        acquisition.delete()
        stdout.p(['Successfully deleted acquisition.'], positions=[1.])

    except Acquisition.DoesNotExist:
        stdout.p(['A acquisition with id "%s" for this issue does not exist.' % id], after='=', positions=[1.])


def edit(issue, id, field, value):
    try:
        acquisition = issue.acquisitions.get(pk=id)
        if field == 'date':
            acquisition.date = value
        elif field == 'price':
            acquisition.price = value
        acquisition.save()
        stdout.p(['Successfully edited acquisition "%s".' % acquisition.id], positions=[1.])
        _print(acquisition)
    except Acquisition.DoesNotExist:
        stdout.p(['A acquisition with id "%s" for this issue does not exist.' % id], after='=', positions=[1.])


def _print(acquisition):
    positions=[.33, 1.]
    stdout.p(['Field', 'Value'], positions=positions, after='=')
    stdout.p(['Id', acquisition.id], positions=positions)
    stdout.p(['Date', acquisition.date], positions=positions)
    stdout.p(['Price', acquisition.price], after='=', positions=positions)
