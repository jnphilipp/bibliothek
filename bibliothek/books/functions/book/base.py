#!/usr/bin/env python3
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

from books.models import Book
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _
from links.models import Link
from genres.models import Genre
from persons.models import Person
from series.models import Series
from utils import lookahead, stdout


def create(title, authors=[], series=None, volume=0, genres=[], links=[]):
    positions = [.33, 1.]

    book, created = Book.objects.get_or_create(title=title)
    if created:
        stdout.p([_('Id'), book.id], positions=positions)
        stdout.p([_('Title'), book.title], positions=positions)

        if len(authors) > 0:
            for (i, a), has_next in lookahead(enumerate(authors)):
                author, c = Person.objects.annotate(
                    name=Concat('first_name', Value(' '), 'last_name')
                ).filter(
                    Q(pk=a if a.isdigit() else None) | Q(name__icontains=a)
                ).get_or_create(
                    defaults={
                        'first_name': a[:a.rfind(' ')],
                        'last_name': a[a.rfind(' ') + 1 :]}
                )
                book.authors.add(author)
                stdout.p([_('Authors') if i == 0 else '',
                          '%s: %s' % (author.id, str(author))],
                         after=None if has_next else '_', positions=positions)
        else:
            stdout.p([_('Authors'), ''], positions=positions)

        if series:
            book.series, c = Series.objects.filter(
                Q(pk=series) if series.isdigit() else Q(name__icontains=series)
            ).get_or_create(defaults={'name': series})
            stdout.p([_('Series'),
                      '%s: %s' % (book.series.id, book.series.name)],
                     positions=positions)
        else:
            stdout.p([_('Series'), ''], positions=positions)

        if volume:
            book.volume = volume
            stdout.p([_('Volume'), book.volume], positions=positions)
        else:
            stdout.p([_('Volume'), ''], positions=positions)

        for (i, g), has_next in lookahead(enumerate(genres)):
            genre, c = Genre.objects.filter(
                Q(pk=g if g.isdigit() else None) | Q(name=g)
            ).get_or_create(defaults={'name': g})
            book.genres.add(genre)
            stdout.p([_('Genres') if i == 0 else '',
                      '%s: %s' % (genre.id, genre.name)],
                     after=None if has_next else '_', positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(
                Q(pk=url if url.isdigit() else None) | Q(link=url)
            ).get_or_create(defaults={'link': url})
            book.links.add(link)
            stdout.p([_('Links') if i == 0 else '',
                      '%s: %s' % (link.id, link.link)],
                     after=None if has_next else '_', positions=positions)

        book.save()

        msg = _('Successfully added book "%(title)s" with id "%(id)s".')
        stdout.p([msg % {'title':book.title, 'id':book.id}], after='=',
                 positions=[1.])
    else:
        msg = _('The book "%(title)s" already exists with id "%(id)s", ' +
                'aborting...')
        stdout.p([msg % {'title':book.title, 'id':book.id}], after='=',
                 positions=[1.])
    return book, created


def edit(book, field, value):
    assert field in ['title', '+author', '-author', 'series', 'volume',
                     '+genre', '-genre', '+link', '-link']

    if field == 'title':
        book.title = value
    elif field == '+author':
        author, created = Person.objects.annotate(
            name=Concat('first_name', Value(' '), 'last_name')
        ).filter(
            Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)
        ).get_or_create(
            defaults={
                'first_name': value[:value.rfind(' ')],
                'last_name': value[value.rfind(' ') + 1 :]}
        )
        book.authors.add(author)
    elif field == '-author':
        try:
            author = Person.objects.annotate(
                name=Concat('first_name', Value(' '), 'last_name')
            ).get(
                Q(pk=value if value.isdigit() else None) |
                Q(name__icontains=value)
            )
            book.authors.remove(author)
        except Person.DoesNotExist:
            stdout.p([_('Author "%(name)s" not found.') % {'name': value}],
                     positions=[1.])
    elif field == 'series':
        book.series, created = Series.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)
        ).get_or_create(defaults={'name': value})
    elif field == 'volume':
        book.volume = value
    elif field == '+genre':
        genre, created = Genre.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(name=value)
        ).get_or_create(defaults={'name': value})
        book.genres.add(genre)
    elif field == '-genre':
        try:
            genre = Genre.objects.get(
                Q(pk=value if value.isdigit() else None) | Q(name=value)
            )
            book.genres.remove(genre)
        except Genre.DoesNotExist:
            stdout.p([_('Genre "%(name)s" not found.') % {'name': value}],
                     positions=[1.])
    elif field == '+link':
        link, created = Link.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(link=value)
        ).get_or_create(defaults={'link': value})
        book.links.add(link)
    elif field == '-link':
        try:
            link = Link.objects.get(
                Q(pk=value if value.isdigit() else None) | Q(link=value)
            )
            book.links.remove(link)
        except Link.DoesNotExist:
            stdout.p([_('Link "%(link)s" not found.') % {'link': value}],
                     positions=[1.])
    book.save()

    msg = _('Successfully edited book "%(title)s" with id "%(id)s".')
    stdout.p([msg % {'title': book.title, 'id': book.id}], positions=[1.])


def info(book):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), book.id], positions=positions)
    stdout.p([_('Title'), book.title], positions=positions)

    if book.authors.count() > 0:
        for (i, author), has_next in lookahead(enumerate(book.authors.all())):
            stdout.p([_('Authors') if i == 0 else '',
                      '%s: %s' % (author.id, str(author))],
                     positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Authors'), ''], positions=positions)

    stdout.p([_('Series'),
              '%s: %s' % (book.series.id,
                          book.series.name) if book.series else ''],
             positions=positions)
    stdout.p([_('Volume'), book.volume if book.volume else ''],
             positions=positions)

    if book.genres.count() > 0:
        for (i, genre), has_next in lookahead(enumerate(book.genres.all())):
            stdout.p([_('Genres') if i == 0 else '', '%s: %s' % (genre.id,
                                                                 genre.name)],
                     positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Genres'), ''], positions=positions)

    if book.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(book.links.all())):
            stdout.p([_('Links') if i == 0 else '', '%s: %s' % (link.id,
                                                                link.link)],
                     positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)

    if book.editions.count() > 0:
        editions = book.editions.all()
        for (i, edition), has_next in lookahead(enumerate(editions)):
            s = ''
            if edition.alternate_title:
                s += '%s, ' % edition.alternate_title
            if edition.isbn:
                s += '%s, ' % edition.isbn
            if edition.binding:
                s += edition.binding.name

            stdout.p([_('Editions') if i == 0 else '', '%s: %s' % (edition.id,
                                                                   s)],
                     positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Editions'), ''], positions=positions)
