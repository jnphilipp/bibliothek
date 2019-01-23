#!/usr/bin/env python3
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

from books.models import Book
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _
from persons.models import Person
from utils import lookahead


def list(books):
    positions = [.05, .5, .75, .9, 1.]
    utils.stdout.p([_('Id'), _('Title'), _('Authors'), _('Series'),
                    _('Volume')], positions=positions, after='=')
    for book, has_next in lookahead(books):
        authors = ' ,'.join(f'{a}' for a in book.authors.all())
        fields = [book.id, book.title, authors,
                  book.series.name if book.series else '',
                  book.volume if book.volume else '']
        utils.stdout.p(fields, positions=positions,
                       after='_' if has_next else '=')


def info(book):
    positions = [.33, 1.]
    utils.stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    utils.stdout.p([_('Id'), book.id], positions=positions)
    utils.stdout.p([_('Title'), book.title], positions=positions)

    if book.authors.count() > 0:
        for (i, author), has_next in lookahead(enumerate(book.authors.all())):
            utils.stdout.p([_('Authors') if i == 0 else '',
                            f'{author.id}: {author}'], positions=positions,
                           after='' if has_next else '_')
    else:
        utils.stdout.p([_('Authors'), ''], positions=positions)

    if book.series:
        utils.stdout.p([_('Series'), f'{book.series.id}: {book.series.name}'],
                       positions=positions)
    else:
        utils.stdout.p([_('Series'), ''], positions=positions)

    if book.volume:
        utils.stdout.p([_('Volume'), book.volume], positions=positions)
    else:
        utils.stdout.p([_('Volume'), ''], positions=positions)

    if book.genres.count() > 0:
        for (i, genre), has_next in lookahead(enumerate(book.genres.all())):
            utils.stdout.p([_('Genres') if i == 0 else '',
                            f'{genre.id}: {genre.name}'], positions=positions,
                           after='' if has_next else '_')
    else:
        utils.stdout.p([_('Genres'), ''], positions=positions)

    if book.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(book.links.all())):
            utils.stdout.p([_('Links') if i == 0 else '',
                            f'{link.id}: {link.link}'], positions=positions,
                           after='' if has_next else '_')
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

            utils.stdout.p([_('Editions') if i == 0 else '',
                            f'{edition.id}: {s}'], positions=positions,
                           after='' if has_next else '_')
    else:
        utils.stdout.p([_('Editions'), ''], positions=positions)
