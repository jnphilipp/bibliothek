# -*- coding: utf-8 -*-
# Copyright (C) 2017-2019 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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
from utils import lookahead


def list(bindings):
    positions = [.05]
    utils.stdout.p([_('Id'), _('Name')], '=', positions)
    for binding, has_next in lookahead(bindings):
        utils.stdout.p([binding.id, binding.name], '_' if has_next else '=',
                 positions)


def info(binding):
    positions = [.33]
    utils.stdout.p([_('Field'), _('Value')], '=', positions)
    utils.stdout.p([_('Id'), binding.id], positions=positions)
    utils.stdout.p([_('Name'), binding.name], positions=positions)
