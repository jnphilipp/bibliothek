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
from shelves.models import Acquisition
from utils import lookahead, stdout


def add(edition, date=None, price=0.0):
    acquisition = Acquisition.objects.create(date=date, price=price,
                                             content_object=edition)
    msg = _('Successfully added acquisition "%(id)s" to edition "%(edition)s".')
    stdout.p([msg % {'id': acquisition.id, 'edition': str(edition)}],
             positions=[1.])
    _print(acquisition)
    return acquisition


def delete(edition, acquisition_id):
    try:
        acquisition = edition.acquisitions.get(pk=acquisition_id)
        _print(acquisition)
        acquisition.delete()
        stdout.p([_('Successfully deleted acquisition.')], positions=[1.])
    except Acquisition.DoesNotExist:
        msg = _('An acquisition with id "%(acquisition)s" for this edition ' +
                 'does not exist.')
        stdout.p([msg % {'acquisition':acquisition_id}], after='=',
                 positions=[1.])


def edit(edition, acquisition_id, field, value):
    assert field in ['date', 'price']

    try:
        acquisition = edition.acquisitions.get(pk=acquisition_id)
        if field == 'date':
            acquisition.date = value
        elif field == 'price':
            acquisition.price = value
        acquisition.save()

        msg = _('Successfully edited acquisition "%(acquisition)s".')
        stdout.p([msg % {'acquisition': acquisition.id}], positions=[1.])
        _print(acquisition)
    except Acquisition.DoesNotExist:
        msg = _('An acquisition with id "%(acquisition)s" for this edition ' +
                'does not exist.')
        stdout.p([msg % {'acquisition': acquisition_id}], after='=',
                 positions=[1.])


def _print(acquisition):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), acquisition.id], positions=positions)
    stdout.p([_('Date'), acquisition.date], positions=positions)
    stdout.p([_('Price'), acquisition.price], after='=', positions=positions)
