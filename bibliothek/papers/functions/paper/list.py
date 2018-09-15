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
from papers.models import Paper
from utils import lookahead, stdout


def all():
    papers = Paper.objects.all()
    _list([[paper.id, paper.title,
            paper.journal.name if paper.journal else None,
            paper.volume] for paper in papers],
          [_('Id'), _('Title'), _('Journal'), _('Volume')],
          positions=[.05, .7, .90])
    return papers


def by_shelf(shelf):
    papers = Paper.objects.all()
    if shelf == 'read':
        papers = papers.filter(reads__isnull=False)
    elif shelf == 'unread':
        papers = papers.filter(reads__isnull=True)
    _list([[paper.id, paper.title,
            paper.journal.name if paper.journal else None,
            paper.volume] for paper in papers],
          [_('Id'), _('Title'), _('Journal'), _('Volume')],
          positions=[.05, .7, .90])
    return papers


def by_term(term):
    papers = Paper.objects.annotate(
        jv=Concat('journal__name', Value(' '), 'volume',
                  output_field=TextField())
    ).filter(
        Q(pk=term if term.isdigit() else None) | Q(title__icontains=term) |
        Q(jv__icontains=term)
    )
    _list([[paper.id, paper.title,
            paper.journal.name if paper.journal else None,
            paper.volume] for paper in papers],
          [_('Id'), _('Title'), _('Journal'), _('Volume')],
          positions=[.05, .7, .90])
    return papers


def _list(papers, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for paper, has_next in lookahead(papers):
        stdout.p(paper, positions=positions, after='_' if has_next else '=')
