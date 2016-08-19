# -*- coding: utf-8 -*-

from books.models import Book
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext as _
from utils import lookahead, stdout


def all():
    books = Book.objects.all()
    _list([[book.title, ','.join(str(author) for author in book.authors.all()), book.series.name if book.series else '', book.volume] for book in books], [_('Title'), _('Authors'), _('Series'), _('Volume')], positions=[.45, .75, .9, 1.])
    return books


def by_shelf(shelf):
    books = Book.objects.all()
    if shelf == 'read':
        books = books.filter(editions__reads__isnull=False)
    elif shelf == 'unread':
        books = books.filter(editions__reads__isnull=True)
    books = books.distinct()
    _list([[book.title, ','.join(str(author) for author in book.authors.all()), book.series.name if book.series else '', book.volume] for book in books], [_('Title'), _('Authors'), _('Series'), _('Volume')], positions=[.45, .75, .9, 1.])
    return books


def by_term(term):
    books = Book.objects.annotate(authors__name=Concat('authors__first_name', Value(' '), 'authors__last_name')).filter(Q(title__icontains=term) | Q(authors__name__icontains=term) | Q(series__name__icontains=term) | Q(volume__icontains=term)).distinct()
    _list([[book.title, ','.join(str(author) for author in book.authors.all()), book.series.name if book.series else '', book.volume] for book in books], [_('Title'), _('Authors'), _('Series'), _('Volume')], positions=[.45, .75, .9, 1.])
    return books


def _list(books, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for book, has_next in lookahead(books):
        stdout.p(book, positions=positions, after='_' if has_next else '=')
