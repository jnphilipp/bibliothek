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


def list(issues):
    positions = [.05, .40, .85]
    utils.stdout.p([_('Id'), _('Magazine'), _('Issue'), _('Publishing date')],
                   '=', positions)
    for issue, has_next in lookahead(issues):
        urils.stdout.p([issue.id, issue.magazine.name, issue.issue,
                  issue.publishing_date], '_' if has_next else '=', positions)


def info(issue):
    positions = [.33]
    utils.stdout.p([_('Field'), _('Value')], '=', positions)
    utils.stdout.p([_('Id'), issue.id], positions=positions)
    utils.stdout.p([_('Magazine'),
                    f'{issue.magazine.id}: {issue.magazine.name}'],
                   positions=positions)
    utils.stdout.p([_('Issue'), issue.issue], positions=positions)
    utils.stdout.p([_('Publishing date'), issue.publishing_date],
                   positions=positions)
    utils.stdout.p([_('Cover'), issue.cover_image], positions=positions)

    if issue.languages.count() > 0:
        for (i, l), has_next in lookahead(enumerate(issue.languages.all())):
            utils.stdout.p(['' if i else _('Languages'), f'{l.id}: {l.name}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Languages'), ''], positions=positions)

    if issue.files.count() > 0:
        for (i, file), has_next in lookahead(enumerate(issue.files.all())):
            utils.stdout.p(['' if i else _('Files'), f'{file.id}: {file}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Files'), ''], positions=positions)

    if issue.links.count() > 0:
        for (i, l), has_next in lookahead(enumerate(issue.links.all())):
            utils.stdout.p(['' if i else _('Links'), f'{l.id}: {l.link}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Links'), ''], positions=positions)

    if issue.acquisitions.count() > 0:
        acquisitions = issue.acquisitions.all()
        date_trans = _('date')
        price_trans = _('price')
        for (i, a), has_next in lookahead(enumerate(acquisitions)):
            s = f'{a.id}: {date_trans}={a.date}, {price_trans}={a.price:0.2f}'
            utils.stdout.p(['' if i else _('Acquisitions'), s],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Acquisitions'), ''], positions=positions)

    if issue.reads.count() > 0:
        ds_trans = _('date started')
        df_trans = _('date finished')
        for (i, r), has_next in lookahead(enumerate(issue.reads.all())):
            s = f'{r.id}: {ds_trans}={r.started}, {df_trans}={r.finished}'
            utils.stdout.p(['' if i else _('Read'), s],
                           '' if has_next else '=', positions)
    else:
        utils.stdout.p([_('Read'), ''], positions=positions)
