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

from django.db.models import Q
from magazines.models import Issue

from . import list as issue_list


def by_pk(pk, magazine=None):
    issues = Issue.objects.all()
    if magazine is not None:
        issues = issues.filter(magazine=magazine)

    try:
        return issues.get(pk=pk)
    except Issue.DoesNotExist:
        return None


def by_term(term, magazine=None):
    issues = issue_list.by_term(term, magazine)

    if issues.count() == 0:
        return None
    elif issues.count() > 1:
        if term.isdigit():
            issues = issues.filter(pk=term)
        else:
            issues = issues.filter(Q(issue=term) | Q(name=term))
        if issues.count() != 1:
            return None
    return issues[0]
