# -*- coding: utf-8 -*-

import re

from datetime import datetime
from django.utils.translation import ugettext as _
from shelves.models import Acquisition
from utils import lookahead, stdout


def add(paper, date=None, price=0.0):
    acquisition = Acquisition.objects.create(date=date, price=price, content_object=paper)
    stdout.p([_('Successfully added acquisition "%(id)s" to paper "%(paper)s".') % {'id':acquisition.id, 'paper':paper.title}], positions=[1.])
    _print(acquisition)
    return acquisition


def delete(paper, acquisition_id):
    try:
        acquisition = paper.acquisitions.get(pk=acquisition_id)
        _print(acquisition)
        acquisition.delete()
        stdout.p([_('Successfully deleted acquisition.')], positions=[1.])
    except Acquisition.DoesNotExist:
        stdout.p([_('A acquisition with id "%(acquisition)s" for this paper does not exist.') % {'acquisition':acquisition_id}], after='=', positions=[1.])


def edit(paper, acquisition_id, field, value):
    assert field in ['date', 'price']

    try:
        acquisition = paper.acquisitions.get(pk=acquisition_id)
        if field == 'date':
            acquisition.date = value
        elif field == 'price':
            acquisition.price = value
        acquisition.save()
        stdout.p([_('Successfully edited acquisition "%(acquisition)s".') % {'acquisition':acquisition.id}], positions=[1.])
        _print(acquisition)
    except Acquisition.DoesNotExist:
        stdout.p(['A acquisition with id "%(acquisition)s" for this paper does not exist.' % {'acquisition':acquisition_id}], after='=', positions=[1.])


def _print(acquisition):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), acquisition.id], positions=positions)
    stdout.p([_('Date'), acquisition.date], positions=positions)
    stdout.p([_('Price'), acquisition.price], after='=', positions=positions)
