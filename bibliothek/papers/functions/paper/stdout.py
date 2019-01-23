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


def list(papers):
    positions = [.05, .7, .90]
    utils.stdout.p([_('Id'), _('Title'), _('Journal'), _('Volume')], '=',
                   positions)
    for paper, has_next in lookahead(papers):
        fields = [paper.id, paper.title,
                  paper.journal.name if paper.journal else None, paper.volume]
        utils.stdout.p(fields, '_' if has_next else '=', positions)


def info(paper):
    positions = [.33]
    utils.stdout.p([_('Field'), _('Value')], '=', positions)
    utils.stdout.p([_('Id'), paper.id], positions=positions)
    utils.stdout.p([_('Title'), paper.title], positions=positions)

    if paper.authors.count() > 0:
        for (i, author), has_next in lookahead(enumerate(paper.authors.all())):
            utils.stdout.p(['' if i else _('Authors'),
                            f'{author.id}: {author}'], '' if has_next else '_',
                           positions)
    else:
        utils.stdout.p([_('Authors'), ''], positions=positions)

    journal = (f'{paper.journal.id}: {paper.journal.name}') \
        if paper.journal else ''
    utils.stdout.p([_('Journal'), journal], positions=positions)
    utils.stdout.p([_('Volume'), paper.volume if paper.volume else ''],
                   positions=positions)
    utils.stdout.p([_('Publishing date'), paper.publishing_date],
                   positions=positions)

    if paper.languages.count() > 0:
        for (i, l), has_next in lookahead(enumerate(paper.languages.all())):
            utils.stdout.p(['' if i else _('Languages'), f'{l.id}: {l}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Languages'), ''], positions=positions)

    if paper.files.count() > 0:
        for (i, file), has_next in lookahead(enumerate(paper.files.all())):
            utils.stdout.p(['' if i else _('Files'), f'{file.id}: {file}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Files'), ''], positions=positions)

    if paper.links.count() > 0:
        for (i, l), has_next in lookahead(enumerate(paper.links.all())):
            utils.stdout.p(['' if i else _('Links'), f'{l.id}: {l.link}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Links'), ''], positions=positions)

    if paper.acquisitions.count() > 0:
        date_trans = _('date')
        price_trans = _('price')
        for (i, a), has_next in lookahead(enumerate(paper.acquisitions.all())):
            s = f'{a.id}: {date_trans}={a.date}, {price_trans}={a.price:0.2f}'
            utils.stdout.p(['' if i else _('Acquisitions'), a],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Acquisitions'), ''], positions=positions)

    if paper.reads.count() > 0:
        ds_trans = _('date started')
        df_trans = _('date finished')
        for (i, r), has_next in lookahead(enumerate(paper.reads.all())):
            s = f'{r.id}: {ds_trans}={r.started}, {df_trans}={r.finished}'
            utils.stdout.p(['' if i else _('Reads'), s],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Reads'), ''], positions=positions)
