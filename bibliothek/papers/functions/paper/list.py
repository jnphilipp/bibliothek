# -*- coding: utf-8 -*-

from django.db.models import Q
from papers.models import Paper
from utils import lookahead, stdout


def by_shelf(shelf):
    papers = Paper.objects.all()
    if shelf == 'read':
        papers = papers.filter(reads__isnull=False)
    elif shelf == 'unread':
        papers = papers.filter(reads__isnull=True)
    _list([[paper.title, paper.journal.name if paper.journal else None, paper.volume] for paper in papers], ['Title', 'Journal', 'Volume'], positions=[.55, .66, 1.])


def by_search(term=None):
    papers = Paper.objects.all()
    if term:
        papers = papers.filter(Q(title__icontains=term) | Q(journal__name__icontains=term) | Q(volume__icontains=term))
    if stdout:
        _list([[paper.id, paper.title, paper.journal.name if paper.journal else None, paper.volume] for paper in papers], ['Id', 'Title', 'Journal', 'Volume'], positions=[.05, .55, .66, 1.])
    return papers


def _list(papers, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for paper, has_next in lookahead(papers):
        stdout.p(paper, positions=positions, after='_' if has_next else '=')