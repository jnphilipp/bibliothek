# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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

from django.db.models import Q, TextField, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _
from magazines.models import Issue
from utils import lookahead, stdout


def all(magazine=None):
    issues = Issue.objects.all().order_by('publishing_date')
    if magazine is not None:
        issues = issues.filter(magazine=magazine)
    _list([[issue.id, issue.magazine.name, issue.issue,
            issue.publishing_date] for issue in issues],
          [_('Id'), _('Magazine'), _('Issue'), _('Publishing date')],
          positions=[.05, .40, .85])
    return issues


def by_shelf(shelf, magazine=None):
    issues = Issue.objects.all()
    if magazine is not None:
        issues = issues.filter(magazine=magazine)
    if shelf == 'read':
        issues = issues.filter(reads__isnull=False)
    elif shelf == 'unread':
        issues = issues.filter(reads__isnull=True)
    _list([[issue.id, issue.magazine.name, issue.issue,
            issue.publishing_date] for issue in issues],
          [_('Id'), _('Magazine'), _('Issue'), _('Publishing date')],
          positions=[.05, .40, .85])
    return issues


def by_term(term, magazine=None):
    issues = Issue.objects.annotate(
        name=Concat('magazine__name', Value(' '), 'issue',
                    output_field=TextField())).all()
    if magazine is not None:
        issues = issues.filter(magazine=magazine)
    issues = issues.filter(Q(pk=term if term.isdigit() else None) |
                           Q(name__icontains=term))
    _list([[issue.id, issue.magazine.name, issue.issue,
            issue.publishing_date] for issue in issues],
          [_('Id'), _('Magazine'), _('Issue'), _('Publishing date')],
          positions=[.05, .40, .85])
    return issues


def _list(issues, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for issue, has_next in lookahead(issues):
        stdout.p(issue, positions=positions, after='_' if has_next else '=')
