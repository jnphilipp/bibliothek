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

from books.models import Book
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _
from links.models import Link
from genres.models import Genre
from persons.models import Person
from series.models import Series
from utils import lookahead


def create(title, authors=[], series=None, volume=0, genres=[], links=[]):
    positions = [.33, 1.]

    book, created = Book.objects.get_or_create(title=title)
    if created:
        for (i, a), has_next in lookahead(enumerate(authors)):
            author, c = Person.objects.annotate(
                name=Concat('first_name', Value(' '), 'last_name')
            ).filter(
                Q(pk=a if a.isdigit() else None) | Q(name__icontains=a)
            ).get_or_create(
                defaults={
                    'first_name': a[:a.rfind(' ')],
                    'last_name': a[a.rfind(' ') + 1:]}
            )
            book.authors.add(author)

        if series:
            book.series, c = Series.objects.filter(
                Q(pk=series) if series.isdigit() else Q(name__icontains=series)
            ).get_or_create(defaults={'name': series})

        if volume:
            book.volume = volume

        for (i, g), has_next in lookahead(enumerate(genres)):
            genre, c = Genre.objects.filter(
                Q(pk=g if g.isdigit() else None) | Q(name=g)
            ).get_or_create(defaults={'name': g})
            book.genres.add(genre)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(
                Q(pk=url if url.isdigit() else None) | Q(link=url)
            ).get_or_create(defaults={'link': url})
            book.links.add(link)
        book.save()
    return book, created


def edit(book, field, value):
    assert field in ['title', 'author', 'series', 'volume', 'genre', 'link']

    if field == 'title':
        book.title = value
    elif field == 'author':
        author, created = Person.objects.annotate(
            name=Concat('first_name', Value(' '), 'last_name')
        ).filter(
            Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)
        ).get_or_create(
            defaults={
                'first_name': value[:value.rfind(' ')],
                'last_name': value[value.rfind(' ') + 1:]}
        )
        if book.authors.filter(pk=author.pk).exists():
            book.authors.remove(author)
        else:
            book.authors.add(author)
    elif field == 'series':
        book.series, created = Series.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)
        ).get_or_create(defaults={'name': value})
    elif field == 'volume':
        book.volume = value
    elif field == 'genre':
        genre, created = Genre.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(name=value)
        ).get_or_create(defaults={'name': value})
        if book.genres.filter(pk=genre.pk).exists():
            book.genres.remove(genre)
        else:
            book.genres.add(genre)
    elif field == 'link':
        link, created = Link.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(link=value)
        ).get_or_create(defaults={'link': value})
        if book.links.filter(pk=link.pk).exists():
            book.links.remove(link)
        else:
            book.links.add(link)
    book.save()
