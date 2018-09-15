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
from utils import stdout

from . import list as series_list


def by_term(term):
    series = series_list.by_term(term)

    if series.count() == 0:
        stdout.p([_('No series found.')], after='=')
        print('\n')
        return None
    elif series.count() > 1:
        if term.isdigit():
            series = series.filter(pk=term)
        else:
            series = series.filter(name=term)
        if series.count() != 1:
            stdout.p([_('More than one series found.')], after='=')
            print('\n')
            return None
    print('\n')
    return series[0]
