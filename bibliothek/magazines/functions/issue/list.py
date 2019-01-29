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

from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _
from magazines.models import Issue
from utils import lookahead


def all(magazine=None):
    issues = Issue.objects.all().order_by('publishing_date')
    if magazine is not None:
        issues = issues.filter(magazine=magazine)
    return issues


def by_shelf(shelf, magazine=None):
    issues = Issue.objects.all()
    if magazine is not None:
        issues = issues.filter(magazine=magazine)
    if shelf == 'read':
        issues = issues.filter(reads__isnull=False)
    elif shelf == 'unread':
        issues = issues.filter(reads__isnull=True)
    return issues.distinct()


def by_term(term, magazine=None, has_file=None):
    issues = Issue.objects.annotate(name=Concat('magazine__name', Value(' '),
                                                'issue')).all()
    if magazine is not None:
        issues = issues.filter(magazine=magazine)
    if has_file is not None:
        issues = issues.filter(files__isnull=not has_file)
    issues = issues.filter(Q(pk=term if term.isdigit() else None) |
                           Q(name__icontains=term))
    return issues
