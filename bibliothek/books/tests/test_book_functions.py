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

from books.functions import book as fbook
from django.test import TestCase
from persons.functions import person as fperson
from series.functions import series as fseries


class BookFunctionsTestCase(TestCase):
    def test_book_create(self):
        book, created = fbook.create('Test Book')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        person, created = fperson.create('Firstname', 'Lastname')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        series, created = fseries.create('Test Series')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        book, created = fbook.create('Some Test Book', [str(person.id)],
                                     str(series.id), 1.0, ['SciFi', 'Romance'])
        self.assertTrue(created)
        self.assertIsNotNone(book.id)
        self.assertEquals(1, book.authors.count())
        self.assertEquals(person, book.authors.first())
        self.assertEquals(series, book.series)
        self.assertEquals(2, book.genres.count())
        self.assertEquals('Romance', book.genres.first().name)
        self.assertEquals('SciFi', book.genres.last().name)

        author = ['%s %s' % (person.first_name, person.last_name)]
        book, created = fbook.create('Some Test Book 2', author, series.name,
                                     1.0, ['SciFi', 'Romance'])
        self.assertTrue(created)
        self.assertIsNotNone(book.id)
        self.assertEquals(1, book.authors.count())
        self.assertEquals(person, book.authors.first())
        self.assertEquals(series, book.series)
        self.assertEquals('Romance', book.genres.first().name)
        self.assertEquals('SciFi', book.genres.last().name)

    def test_book_edit(self):
        series, created = fseries.create('Test Series')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        person, created = fperson.create('John', 'Do')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        book, created = fbook.create('Test2 Book', [str(person.id)],
                                     series=str(series.id), volume=1.0,
                                     genres=['Romance'])
        self.assertTrue(created)
        self.assertIsNotNone(book.id)
        self.assertEquals(series, book.series)

        fbook.edit(book, 'title', 'IEEE Test Book')
        self.assertEquals('IEEE Test Book', book.title)

        fbook.edit(book, 'author', 'Jane Do')
        self.assertEquals(2, book.authors.count())
        self.assertEquals('Jane Do', str(book.authors.all()[0]))
        self.assertEquals('John Do', str(book.authors.all()[1]))

        fbook.edit(book, 'author', str(person.id))
        self.assertEquals(1, book.authors.count())
        self.assertEquals('Jane Do', str(book.authors.all()[0]))

        series, created = fseries.create('Space Series')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        fbook.edit(book, 'series', str(series.id))
        self.assertEquals(series, book.series)

        fbook.edit(book, 'volume', 0.75)
        self.assertEquals(0.75, book.volume)

        series, created = fseries.create('Deep Space Series')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        fbook.edit(book, 'series', 'Deep Space')
        self.assertEquals(series, book.series)

        fbook.edit(book, 'genre', 'SciFi')
        self.assertEquals(2, book.genres.count())
        self.assertEquals('Romance', book.genres.first().name)
        self.assertEquals('SciFi', book.genres.last().name)

        fbook.edit(book, 'genre', '1')
        self.assertEquals(1, book.genres.count())
        self.assertEquals('SciFi', book.genres.first().name)

        fbook.edit(book, 'link', 'https://deep.space')
        self.assertEquals(1, book.links.count())
        self.assertEquals('https://deep.space', book.links.first().link)

        fbook.edit(book, 'link', 'https://janedo.com/test2book')
        self.assertEquals(2, book.links.count())
        self.assertEquals('https://janedo.com/test2book',
                          book.links.last().link)

        fbook.edit(book, 'link', 'https://deep.space')
        self.assertEquals(1, book.links.count())
        self.assertEquals('https://janedo.com/test2book',
                          book.links.first().link)

    def test_book_get(self):
        book, created = fbook.create('Test Book')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        book2 = fbook.get.by_term('Test Book')
        self.assertIsNotNone(book2)
        self.assertEquals(book, book2)

        book2 = fbook.get.by_term(str(book.id))
        self.assertIsNotNone(book2)
        self.assertEquals(book, book2)

    def test_book_list(self):
        book, created = fbook.create('About Stuff')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        book, created = fbook.create('Not so cool Stuff')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        book, created = fbook.create('About cool Stuff')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        books = fbook.list.all()
        self.assertEquals(3, len(books))

        books = fbook.list.by_term('cool Stuff')
        self.assertEquals(2, len(books))
