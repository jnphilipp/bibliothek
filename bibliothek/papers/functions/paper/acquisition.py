# -*- coding: utf-8 -*-

import re

from datetime import datetime
from papers.models import Paper
from shelves.models import Acquisition
from utils import lookahead, stdout


def add(paper, date=None, price=0.0):
    acquisition = Acquisition.objects.create(date=date, price=price, content_object=paper)
    stdout.p(['Successfully added acquisition "%s" to paper "%s".' % (acquisition.id, paper.title)], positions=[1.])
    _print(acquisition)
    return acquisition


def delete(paper, id):
    try:
        acquisition = paper.acquisitions.get(pk=id)
        _print(acquisition)
        acquisition.delete()
        stdout.p(['Successfully deleted acquisition.'], positions=[1.])
    except Acquisition.DoesNotExist:
        stdout.p(['A acquisition with id "%s" for this paper does not exist.' % id], after='=', positions=[1.])


def edit(paper, id, field, value):
    assert field in ['date', 'price']

    try:
        acquisition = paper.acquisitions.get(pk=id)
        if field == 'date':
            acquisition.date = value
        elif field == 'price':
            acquisition.price = value
        acquisition.save()
        stdout.p(['Successfully edited acquisition "%s".' % acquisition.id], positions=[1.])
        _print(acquisition)
        return acquisition
    except Acquisition.DoesNotExist:
        stdout.p(['A acquisition with id "%s" for this paper does not exist.' % id], after='=', positions=[1.])
        return None


def _print(acquisition):
    positions=[.33, 1.]
    stdout.p(['Field', 'Value'], positions=positions, after='=')
    stdout.p(['Id', acquisition.id], positions=positions)
    stdout.p(['Date', acquisition.date], positions=positions)
    stdout.p(['Price', acquisition.price], after='=', positions=positions)
