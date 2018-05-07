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

from bindings.functions import binding as fbinding
from books.functions import book as fbook, edition as fedition
from django.test import TestCase
from publishers.functions import publisher as fpublisher


class BookFunctionsTestCase(TestCase):
    def setUp(self):
        self.book, created = fbook.create('A book about something',
                                          ['John Do'], 'Some Series', 1)
        self.assertTrue(created)
        self.assertIsNotNone(self.book.id)
        self.assertEquals(1, self.book.authors.count())
        self.assertIsNotNone(self.book.authors.first().id)
        self.assertEquals('John', self.book.authors.first().first_name)
        self.assertEquals('Do', self.book.authors.first().last_name)
        self.assertIsNotNone(self.book.series.id)
        self.assertEquals('Some Series', self.book.series.name)
        self.assertEquals(1, self.book.volume)

    def test_book_create(self):
        binding, created = fbinding.create('Taschenbuch')
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

        publisher, created = fpublisher.create('Book Printer')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        edition, created = fedition.create(self.book)
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)
        self.assertIsNone(edition.isbn)
        self.assertIsNone(edition.publishing_date)
        self.assertIsNone(edition.binding)
        self.assertIsNone(edition.publisher)

        edition, created = fedition.create(self.book, isbn='9783555464652',
                                           publishing_date='2016-05-01',
                                           binding=str(binding.id),
                                           publisher=str(publisher.id))
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)
        self.assertEquals('9783555464652', edition.isbn)
        self.assertEquals('2016-05-01', edition.publishing_date)
        self.assertEquals(binding, edition.binding)
        self.assertEquals(publisher, edition.publisher)

        edition, created = fedition.create(self.book, isbn='9783365469875',
                                           publishing_date='2016-06-01',
                                           binding='Taschenbuch',
                                           publisher='Book Printer',
                                           languages=['Deutsch', 'Español'])
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)
        self.assertEquals('9783365469875', edition.isbn)
        self.assertEquals('2016-06-01', edition.publishing_date)
        self.assertEquals(binding, edition.binding)
        self.assertEquals(publisher, edition.publisher)
        self.assertEquals(2, edition.languages.count())
        self.assertEquals('Deutsch', edition.languages.first().name)
        self.assertEquals('Español', edition.languages.last().name)

        edition, created = fedition.create(self.book, binding='Paperpback',
                                           publishing_date='2016-06-01',
                                           publisher='Printers',
                                           languages=['English'])
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)
        self.assertIsNone(edition.isbn)
        self.assertEquals('2016-06-01', edition.publishing_date)
        self.assertIsNotNone(edition.binding)
        self.assertIsNotNone(edition.binding.id)
        self.assertIsNotNone(edition.publisher)
        self.assertIsNotNone(edition.publisher.id)
        self.assertEquals(1, edition.languages.count())
        self.assertEquals('English', edition.languages.first().name)

    def test_book_edit(self):
        edition, created = fedition.create(self.book)
        self.assertTrue(created)

        fedition.edit(edition, 'isbn', '9785423647891')
        self.assertEquals('9785423647891', edition.isbn)

        fedition.edit(edition, 'publishing_date', '2016-06-15')
        self.assertEquals('2016-06-15', edition.publishing_date)

        fedition.edit(edition, 'binding', 'Taschenbuch')
        self.assertIsNotNone(edition.binding)
        self.assertIsNotNone(edition.binding.id)
        self.assertEquals('Taschenbuch', edition.binding.name)

        fedition.edit(edition, 'publisher', 'Printers')
        self.assertIsNotNone(edition.publisher)
        self.assertIsNotNone(edition.publisher.id)
        self.assertEquals('Printers', edition.publisher.name)

        fedition.edit(edition, 'language', 'English')
        self.assertEquals(1, edition.languages.count())
        self.assertEquals('English', edition.languages.first().name)

        fedition.edit(edition, 'language', 'Deutsch')
        self.assertEquals(2, edition.languages.count())
        self.assertEquals('Deutsch', edition.languages.first().name)

        fedition.edit(edition, 'language', 'English')
        self.assertEquals(1, edition.languages.count())
        self.assertEquals('Deutsch', edition.languages.first().name)

    def test_book_get(self):
        edition, created = fedition.create(self.book, '9783365469875',
                                           '2016-06-01')
        self.assertTrue(created)

        edition2, created = fedition.create(self.book,
                                            publishing_date='2016-06-02')
        self.assertTrue(created)

        e = fedition.get.by_term(self.book, '9783365469875')
        self.assertIsNotNone(e)
        self.assertEquals(edition, e)

        e = fedition.get.by_term(self.book, '2016-06-02')
        self.assertIsNotNone(e)
        self.assertEquals(edition2, e)

    def test_book_list(self):
        edition, created = fedition.create(self.book)
        self.assertTrue(created)

        edition, created = fedition.create(self.book, '9783555464652',
                                           '2016-05-01')
        self.assertTrue(created)

        edition, created = fedition.create(self.book, '9783365469875',
                                           '2016-06-01')
        self.assertTrue(created)

        edition, created = fedition.create(self.book,
                                           publishing_date='2016-06-01')
        self.assertTrue(created)

        editions = fedition.list.all(self.book)
        self.assertEquals(4, len(editions))

        editions = fedition.list.by_term(self.book, '978')
        self.assertEquals(2, len(editions))

        editions = fedition.list.by_term(self.book, '2016-06')
        self.assertEquals(2, len(editions))

    def test_edition_acquisition(self):
        edition, created = fedition.create(self.book)
        self.assertTrue(created)

        acquisition = fedition.acquisition.add(edition, date='2016-06-02',
                                               price=2.5)
        self.assertIsNotNone(acquisition)
        self.assertIsNotNone(acquisition.id)
        self.assertEquals(1, edition.acquisitions.count())

        fedition.acquisition.edit(edition, acquisition.id, 'price', 5.75)
        self.assertIsNotNone(5.75, acquisition.price)

        fedition.acquisition.delete(edition, acquisition.id)
        self.assertEquals(0, edition.acquisitions.count())

    def test_edition_read(self):
        edition, created = fedition.create(self.book)
        self.assertTrue(created)

        read = fedition.read.add(edition, started='2016-07-03')
        self.assertIsNotNone(read)
        self.assertIsNotNone(read.id)
        self.assertEquals(1, edition.reads.count())

        fedition.read.edit(edition, read.id, 'started', '2016-07-05')
        self.assertIsNotNone('2016-07-05', str(read.started))

        fedition.read.edit(edition, read.id, 'finished', '2016-07-15')
        self.assertIsNotNone('2016-07-15', str(read.finished))

        fedition.read.delete(edition, read.id)
        self.assertEquals(edition.reads.count(), 0)
