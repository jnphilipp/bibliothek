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

from shelves.models import Read

from . import list as read_list


def by_pk(pk, edition=None, paper=None):
    reads = Read.objects.all()
    if edition is not None:
        reads = reads.filter(editions=edition)
    if paper is not None:
        reads = reads.filter(papers=paper)

    try:
        return reads.get(pk=pk)
    except Read.DoesNotExist:
        return None


def by_term(term):
    reads = read_list.by_term(term)

    if reads.count() == 0:
        return None
    elif reads.count() > 1:
        if term.isdigit():
            reads = reads.filter(pk=term)
        else:
            reads = reads.filter(Q(editions__alternate_title=term) |
                                 Q(editions__isbn=term) | Q(ni=term) |
                                 Q(editions__book__title=term) | Q(jv=term) |
                                 Q(papers__title=term))
        if reads.count() != 1:
            return None
    return reads[0]
