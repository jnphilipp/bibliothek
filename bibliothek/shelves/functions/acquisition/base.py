# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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

from shelves.models import Acquisition


def create(obj, date=None, price=None):
    return Acquisition.objects.create(date=date, price=price,
                                      content_object=obj)


def delete(acquisition):
    acquisition.delete()


def edit(acquisition, field, value):
    assert field in ['date', 'price']

    if field == 'date':
        acquisition.date = value
    elif field == 'price':
        acquisition.price = value
    acquisition.save()
