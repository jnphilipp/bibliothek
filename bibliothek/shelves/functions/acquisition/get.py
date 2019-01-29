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

from shelves.models import Acquisition

from . import list as acquisition_list


def by_pk(pk, edition=None, issue=None, paper=None):
    acquisitions = Acquisition.objects.all()
    if edition is not None:
        acquisitions = acquisitions.filter(editions=edition)
    if issue is not None:
        acquisitions = acquisitions.filter(issues=issue)
    if paper is not None:
        acquisitions = acquisitions.filter(papers=paper)

    try:
        return acquisitions.get(pk=pk)
    except Acquisition.DoesNotExist:
        return None


def by_term(term):
    acqus = acquisition_list.by_term(term)

    if acqus.count() == 0:
        return None
    elif acqus.count() > 1:
        if term.isdigit():
            acqus = acqus.filter(pk=term)
        else:
            acqus = acqus.filter(Q(ni=term) | Q(jv=term) |
                                 Q(editions__isbn=term) |
                                 Q(editions__book__title=term) |
                                 Q(papers__title=term) |
                                 Q(editions__alternate_title=term))
        if acqus.count() != 1:
            return None
    return acqus[0]
