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


def list(editions):
    positions = [.05, .55, .7, .85]
    utils.stdout.p([_('Id'), _('Title'), _('Binding'), _('ISBN'),
                    _('Publishing date')], '=', positions)
    for edition, has_next in lookahead(editions):
        utils.stdout.p([edition.id, edition.get_title(), edition.binding,
                        edition.isbn, edition.publishing_date],
                       '_' if has_next else '=', positions)


def info(edition):
    positions = [.33]
    utils.stdout.p([_('Field'), _('Value')], '=', positions)
    utils.stdout.p([_('Id'), edition.id], positions=positions)
    utils.stdout.p([_('Book'), f'{edition.book}'], positions=positions)
    utils.stdout.p([_('Alternate title'), edition.alternate_title],
                   positions=positions)
    utils.stdout.p([_('ISBN'), edition.isbn], positions=positions)
    utils.stdout.p([_('Publishing date'), edition.publishing_date],
                   positions=positions)
    utils.stdout.p([_('Cover'), edition.cover_image], positions=positions)

    binding = f'{edition.binding.id}: {edition.binding.name}' \
        if edition.binding else ''
    utils.stdout.p([_('Binding'), binding], positions=positions)

    publisher = f'{edition.publisher.id}: {edition.publisher.name}' \
        if edition.publisher else ''
    utils.stdout.p([_('Publisher'), publisher], positions=positions)

    if edition.persons.count() > 0:
        for (i, p), has_next in lookahead(enumerate(edition.languages.all())):
            utils.stdout.p(['' if i else _('Persons'), f'{p.id}: {p}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Persons'), ''], positions=positions)

    if edition.languages.count() > 0:
        for (i, l), has_next in lookahead(enumerate(edition.languages.all())):
            utils.stdout.p(['' if i else _('Languages'), f'{l.id}: {l.name}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Languages'), ''], positions=positions)

    if edition.links.count() > 0:
        for (i, l), has_next in lookahead(enumerate(edition.links.all())):
            utils.stdout.p(['' if i else _('Links'), f'{l.id}: {l.link}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Links'), ''], positions=positions)

    if edition.files.count() > 0:
        for (i, f), has_next in lookahead(enumerate(edition.files.all())):
            utils.stdout.p(['' if i else _('Files'), f'{f.id}: {f}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Files'), ''], positions=positions)

    if edition.acquisitions.count() > 0:
        acquisitions = edition.acquisitions.all()
        date_trans = _('date')
        price_trans = _('price')
        for (i, a), has_next in lookahead(enumerate(acquisitions)):
            s = f'{a.id}: {date_trans}={a.date}, {price_trans}={a.price:0.2f}'
            utils.stdout.p(['' if i else _('Acquisitions'), s],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Acquisitions'), ''], positions=positions)

    if edition.reads.count() > 0:
        ds_trans = _('date started')
        df_trans = _('date finished')
        for (i, r), has_next in lookahead(enumerate(edition.reads.all())):
            s = f'{r.id}: {ds_trans}={r.started}, {df_trans}={r.finished}'
            utils.stdout.p(['' if i else _('Read'), s],
                           '' if has_next else '=', positions)
    else:
        utils.stdout.p([_('Read'), ''], positions=positions)
