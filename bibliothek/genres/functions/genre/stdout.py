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


def list(genres):
    positions = [.05]
    utils.stdout.p([_('Id'), _('Name')], '=', positions)
    for genres, has_next in lookahead(genres):
        utils.stdout.p([genre.id, genre.name], '_' if has_next else '=',
                       positions)


def info(genre):
    positions = [.33]
    stdout.p([_('Field'), _('Value')], '=', positions)
    stdout.p([_('Id'), genre.id], positions=positions)
    stdout.p([_('Name'), genre.name], positions=positions)

    if genre.books.count() > 0:
        for (i, book), has_next in lookahead(enumerate(genre.books.all())):
            stdout.p(['' if i else _('Books'), f'{book.id}: {book}'],
                     '' if has_next else '_', positions)
    else:
        stdout.p([_('Books'), ''], positions=positions)
