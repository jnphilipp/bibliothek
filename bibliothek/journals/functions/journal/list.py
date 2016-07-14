# -*- coding: utf-8 -*-

from django.db.models import Q
from journals.models import Journal
from utils import lookahead, stdout


def by_shelf(shelf):
    journals = Journal.objects.all()
    if shelf == 'read':
        journals = journals.filter(papers__reads__isnull=False)
    elif shelf == 'unread':
        journals = journals.filter(papers__reads__isnull=True)
    journals = journals.distinct()
    _list([[journal.id, journal.name, journal.papers.count()] for journal in journals], ['Id', 'Name', '#Papers'], positions=[.05, .55, 1.])


def by_search(term=None):
    journals = Journal.objects.all()
    if term:
        journals = journals.filter(Q(name__icontains=term) | Q(papers__title__icontains=term) | Q(papers__volume__icontains=term))
    journals = journals.distinct()
    if stdout:
        _list([[journal.id, journal.name, journal.papers.count()] for journal in journals], ['Id', 'Name', '#Papers'], positions=[.05, .55, 1.])


def _list(journals, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for journal, has_next in lookahead(journals):
        stdout.p(journal, positions=positions, after='_' if has_next else '=')
