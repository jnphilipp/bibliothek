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


def list(persons):
    positions = [.05, .8, .9]
    utils.stdout.p([_('Id'), _('Name'), _('#Books'), _('#Papers')], '=',
                   positions)
    for person, has_next in lookahead(persons):
        utils.stdout.p([person.id, person.name, person.books.count(),
                       person.papers.count()], '_' if has_next else '=',
                       positions)


def info(person):
    positions = [.33]
    utils.stdout.p([_('Field'), _('Value')], '=', positions)
    utils.stdout.p([_('Id'), person.id], positions=positions)
    utils.stdout.p([_('Name'), person.name], positions=positions)

    if person.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(person.links.all())):
            utils.stdout.p(['' if i else _('Links'),
                            f'{link.id}: {link.link}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Links'), ''], positions=positions)

    if person.books.count() > 0:
        for (i, b), has_next in lookahead(enumerate(person.books.all())):
            utils.stdout.p(['' if i else _('Books'), f'{b.id}: {b.title}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Books'), ''], positions=positions)

    if person.papers.count() > 0:
        for (i, p), has_next in lookahead(enumerate(person.papers.all())):
            utils.stdout.p([''if i else _('Papers'), f'{p.id}: {p.title}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Papers'), ''], positions=positions)
