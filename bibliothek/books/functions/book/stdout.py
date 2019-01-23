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


def list(books):
    positions = [.05, .5, .75, .9]
    utils.stdout.p([_('Id'), _('Title'), _('Authors'), _('Series'),
                    _('Volume')], '=', positions)
    for book, has_next in lookahead(books):
        authors = ' ,'.join(f'{a}' for a in book.authors.all())
        fields = [book.id, book.title, authors,
                  book.series.name if book.series else '', book.volume]
        utils.stdout.p(fields, '_' if has_next else '=', positions)


def info(book):
    positions = [.33]
    utils.stdout.p([_('Field'), _('Value')], '=', positions)
    utils.stdout.p([_('Id'), book.id], positions=positions)
    utils.stdout.p([_('Title'), book.title], positions=positions)

    if book.authors.count() > 0:
        for (i, a), has_next in lookahead(enumerate(book.authors.all())):
            utils.stdout.p(['' if i else _('Authors'), f'{a.id}: {a}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Authors'), ''], positions=positions)

    series = f'{book.series.id}: {book.series.name}' if book.series else ''
    utils.stdout.p([_('Series'), series], positions=positions)
    utils.stdout.p([_('Volume'), book.volume], positions=positions)

    if book.genres.count() > 0:
        for (i, g), has_next in lookahead(enumerate(book.genres.all())):
            utils.stdout.p(['' if i else _('Genres'), f'{g.id}: {g.name}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Genres'), ''], positions=positions)

    if book.links.count() > 0:
        for (i, l), has_next in lookahead(enumerate(book.links.all())):
            utils.stdout.p(['' if i else _('Links'), f'{l.id}: {l.link}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Links'), ''], positions=positions)

    if book.editions.count() > 0:
        editions = book.editions.all()
        for (i, edition), has_next in lookahead(enumerate(editions)):
            s = ''
            if edition.alternate_title:
                s = f'{edition.alternate_title}, '
            if edition.isbn:
                s += f'{s}{edition.isbn}, '
            if edition.binding:
                s += edition.binding.name

            utils.stdout.p(['' if i else _('Editions'), f'{edition.id}: {s}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Editions'), ''], positions=positions)
