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

from django.utils.translation import ugettext_lazy as _
from utils import stdout

from . import list as magazine_list


def by_term(term):
    magazines = magazine_list.by_term(term)

    if magazines.count() == 0:
        stdout.p([_('No magazine found.')], after='=')
        print('\n')
        return None
    elif magazines.count() > 1:
        if term.isdigit():
            magazines = magazines.filter(pk=term)
        else:
            magazines = magazines.filter(name=term)
        if magazines.count() != 1:
            stdout.p([_('More than one magazine found.')], after='=')
            print('\n')
            return None
    print('\n')
    return magazines[0]
