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
from utils import lookahead, stdout


def list(magazines):
    positions = [.05, .8]
    utils.stdout.p([_('Id'), _('Name'), _('#Issues')], '=', positions)
    for magazine, has_next in lookahead(magazines):
        utils.stdout.p([magazine.id, magazine.name, magazine.issues.count()],
                 '_' if has_next else '=', positions)


def info(magazine):
    positions = [.33]
    utils.stdout.p([_('Field'), _('Value')], '=', positions)
    utils.stdout.p([_('Id'), magazine.id], positions=positions)
    utils.stdout.p([_('Name'), magazine.name], positions=positions)
    utils.stdout.p([_('Feed'), f'{magazine.feed.id}: {magazine.feed.link}' if
                    magazine.feed else ''], positions=positions)

    if magazine.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(magazine.links.all())):
            utils.stdout.p(['' if i else _('Links'),
                            f'{link.id}: {link.link}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Links'), ''], positions=positions)

    if magazine.issues.count() > 0:
        issues = magazine.issues.all().order_by('publishing_date')
        for (i, issue), has_next in lookahead(enumerate(issues)):
            utils.stdout.p(['' if i else _('Issue'),
                            f'{issue.id}: {issue.issue}'],
                           '' if has_next else '_', positions)
    else:
        utils.stdout.p([_('Issue'), ''], positions=positions)
