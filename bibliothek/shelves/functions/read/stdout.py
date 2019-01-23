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

import utils

from django.utils.translation import ugettext_lazy as _


def list(reads):
    positions = [.05, .7, .85]
    utils.stdout.p([_('Id'), _('Obj'), _('Date started'), _('Date finished')],
                   '=', positions)
    for read, has_next in lookahead(reads):
        stdout.p([read.id, read.content_object, read.started, read.finished],
                 '_' if has_next else '=', positions)


def info(read):
    positions = [.33]
    utils.stdout.p([_('Field'), _('Value')], '=', positions)
    utils.stdout.p([_('Id'), read.id], positions=positions)
    utils.stdout.p([_('Obj'), read.content_object], positions=positions)
    utils.stdout.p([_('Date started'), read.started], positions=positions)
    utils.stdout.p([_('Date finished'), read.finished], positions=positions)
