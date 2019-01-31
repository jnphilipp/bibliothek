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
from utils import lookahead


def list(journals):
    positions = [.05, .9]
    utils.stdout.p([_('Id'), _('Name'), _('#Papers')], '=', positions)
    for journal, has_next in lookahead(journals):
        utils.stdout.p([journal.id, journal.name, journal.papers.count()],
                       '_' if has_next else '=', positions)


def info(journal):
    positions = [.33]
    utils.stdout.p([_('Field'), _('Value')], '=', positions)
    utils.stdout.p([_('Id'), journal.id], positions=positions)
    utils.stdout.p([_('Name'), journal.name], positions=positions)

    if journal.links.count() > 0:
        for (i, l), has_next in lookahead(enumerate(journal.links.all())):
            utils.stdout.p(['' if i else _('Links'), f'{l.id}: {l.link}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Links'), ''], positions=positions)

    if journal.papers.count() > 0:
        for (i, p), has_next in lookahead(enumerate(journal.papers.all())):
            utils.stdout.p(['' if i else _('Papers'), f'{p.id}: {p.title}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Papers'), ''], positions=positions)
