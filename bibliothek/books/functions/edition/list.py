# -*- coding: utf-8 -*-

from books.models import Edition
from django.db.models import Q
from django.utils.translation import ugettext as _
from utils import lookahead, stdout


def all(book):
    editions = Edition.objects.filter(book=book)
    _list([[edition.id, edition.alternate_title, edition.isbn, edition.published_on] for edition in editions], [_('Id'), _('Alternate title'), _('ISBN'), _('Published on')], positions=[.05, .55, .75, 1.])
    return editions


def by_shelf(book, shelf):
    editions = Book.objects.filter(book=book)
    if shelf == 'read':
        editions = editions.filter(reads__isnull=False)
    elif shelf == 'unread':
        editions = editions.filter(Q(reads__isnull=True) | Q(reads__finished__isnull=True))
    editions = editions.distinct()
    _list([[edition.id, edition.alternate_title, edition.isbn, edition.published_on] for edition in editions], [_('Id'), _('Alternate title'), _('ISBN'), _('Published on')], positions=[.05, .55, .75, 1.])
    return editions


def by_term(book, term):
    editions = Edition.objects.filter(Q(book=book) & (Q(pk=term if term.isdigit() else None) | Q(isbn__icontains=term) | Q(published_on__icontains=term)))
    _list([[edition.id, edition.alternate_title, edition.isbn, edition.published_on] for edition in editions], [_('Id'), _('Alternate title'), _('ISBN'), _('Published on')], positions=[.05, .55, .75, 1.])
    return editions


def _list(editions, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for book, has_next in lookahead(editions):
        stdout.p(book, positions=positions, after='_' if has_next else '=')
