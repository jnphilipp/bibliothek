# -*- coding: utf-8 -*-

from books.models import Book
from django.db.models import Q
from django.utils.translation import ugettext as _
from utils import lookahead, stdout


def all():
    books = Book.objects.all()
    _list([[book.id, book.title, ','.join(str(author) for author in book.authors.all()), book.series.name if book.series else '', book.volume] for book in books], [_('Id'), _('Title'), _('Authors'), _('Series'), _('Volume')], positions=[.05, .5, .75, .9, 1.])
    return books


def by_shelf(shelf):
    books = Book.objects.all()
    if shelf == 'read':
        books = books.filter(editions__reads__isnull=False)
    elif shelf == 'unread':
        books = books.filter(editions__reads__isnull=True)
    books = books.distinct()
    _list([[book.id, book.title, ','.join(str(author) for author in book.authors.all()), book.series.name if book.series else '', book.volume] for book in books], [_('Id'), _('Title'), _('Authors'), _('Series'), _('Volume')], positions=[.05, .5, .75, .9, 1.])
    return books


def by_term(term):
    books = Book.objects.filter(Q(pk=term if term.isdigit() else None) | Q(title__icontains=term))
    _list([[book.id, book.title, ','.join(str(author) for author in book.authors.all()), book.series.name if book.series else '', book.volume] for book in books], [_('Id'), _('Title'), _('Authors'), _('Series'), _('Volume')], positions=[.05, .5, .75, .9, 1.])
    return books


def _list(books, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for book, has_next in lookahead(books):
        stdout.p(book, positions=positions, after='_' if has_next else '=')
