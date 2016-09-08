# -*- coding: utf-8 -*-

from bindings import functions as bfunctions
from books import functions
from django.test import TestCase
from publishers import functions as pfunctions


class BookFunctionsTestCase(TestCase):
    def setUp(self):
        self.book, created = functions.book.create('A book about something', ['John Do'], 'Some Series', 1)
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
        binding, created = bfunctions.binding.create('Taschenbuch')
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

        publisher, created = pfunctions.publisher.create('Book Printer')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        edition, created = functions.edition.create(self.book)
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)
        self.assertIsNone(edition.isbn)
        self.assertIsNone(edition.published_on)
        self.assertIsNone(edition.binding)
        self.assertIsNone(edition.publisher)

        edition, created = functions.edition.create(self.book, '9783555464652', '2016-05-01', binding=str(binding.id), publisher=str(publisher.id))
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)
        self.assertEquals('9783555464652', edition.isbn)
        self.assertEquals('2016-05-01', edition.published_on)
        self.assertEquals(binding, edition.binding)
        self.assertEquals(publisher, edition.publisher)

        edition, created = functions.edition.create(self.book, '9783365469875', '2016-06-01', binding='Taschenbuch', publisher='Book Printer', languages=['Deutsch', 'Español'])
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)
        self.assertEquals('9783365469875', edition.isbn)
        self.assertEquals('2016-06-01', edition.published_on)
        self.assertEquals(binding, edition.binding)
        self.assertEquals(publisher, edition.publisher)
        self.assertEquals(2, edition.languages.count())
        self.assertEquals('Deutsch', edition.languages.first().name)
        self.assertEquals('Español', edition.languages.last().name)

        edition, created = functions.edition.create(self.book, published_on='2016-06-01', binding='Paperpback', publisher='Printers', languages=['English'])
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)
        self.assertIsNone(edition.isbn)
        self.assertEquals('2016-06-01', edition.published_on)
        self.assertIsNotNone(edition.binding)
        self.assertIsNotNone(edition.binding.id)
        self.assertIsNotNone(edition.publisher)
        self.assertIsNotNone(edition.publisher.id)
        self.assertEquals(1, edition.languages.count())
        self.assertEquals('English', edition.languages.first().name)


    def test_book_edit(self):
        edition, created = functions.edition.create(self.book)
        self.assertTrue(created)

        functions.edition.edit(edition, 'isbn', '9785423647891')
        self.assertEquals('9785423647891', edition.isbn)

        functions.edition.edit(edition, 'published_on', '2016-06-15')
        self.assertEquals('2016-06-15', edition.published_on)

        functions.edition.edit(edition, 'binding', 'Taschenbuch')
        self.assertIsNotNone(edition.binding)
        self.assertIsNotNone(edition.binding.id)
        self.assertEquals('Taschenbuch', edition.binding.name)

        functions.edition.edit(edition, 'publisher', 'Printers')
        self.assertIsNotNone(edition.publisher)
        self.assertIsNotNone(edition.publisher.id)
        self.assertEquals('Printers', edition.publisher.name)

        functions.edition.edit(edition, '+language', 'English')
        self.assertEquals(1, edition.languages.count())
        self.assertEquals('English', edition.languages.first().name)

        functions.edition.edit(edition, '+language', 'Deutsch')
        self.assertEquals(2, edition.languages.count())
        self.assertEquals('Deutsch', edition.languages.first().name)

        functions.edition.edit(edition, '-language', 'English')
        self.assertEquals(1, edition.languages.count())
        self.assertEquals('Deutsch', edition.languages.first().name)


    def test_book_get(self):
        edition, created = functions.edition.create(self.book, '9783365469875', '2016-06-01')
        self.assertTrue(created)

        edition2, created = functions.edition.create(self.book, published_on='2016-06-02')
        self.assertTrue(created)

        e = functions.edition.get.by_term(self.book, '9783365469875')
        self.assertIsNotNone(e)
        self.assertEquals(edition, e)

        e = functions.edition.get.by_term(self.book, '2016-06-02')
        self.assertIsNotNone(e)
        self.assertEquals(edition2, e)


    def test_book_list(self):
        edition, created = functions.edition.create(self.book)
        self.assertTrue(created)

        edition, created = functions.edition.create(self.book, '9783555464652', '2016-05-01')
        self.assertTrue(created)

        edition, created = functions.edition.create(self.book, '9783365469875', '2016-06-01')
        self.assertTrue(created)

        edition, created = functions.edition.create(self.book, published_on='2016-06-01')
        self.assertTrue(created)

        editions = functions.edition.list.all(self.book)
        self.assertEquals(4, len(editions))

        editions = functions.edition.list.by_term(self.book, '978')
        self.assertEquals(2, len(editions))

        editions = functions.edition.list.by_term(self.book, '2016-06')
        self.assertEquals(2, len(editions))


    def test_edition_acquisition(self):
        edition, created = functions.edition.create(self.book)
        self.assertTrue(created)

        acquisition = functions.edition.acquisition.add(edition, date='2016-06-02', price=2.5)
        self.assertIsNotNone(acquisition)
        self.assertIsNotNone(acquisition.id)
        self.assertEquals(1, edition.acquisitions.count())

        functions.edition.acquisition.edit(edition, acquisition.id, 'price', 5.75)
        self.assertIsNotNone(5.75, acquisition.price)

        functions.edition.acquisition.delete(edition, acquisition.id)
        self.assertEquals(0, edition.acquisitions.count())


    def test_edition_read(self):
        edition, created = functions.edition.create(self.book)
        self.assertTrue(created)

        read = functions.edition.read.add(edition, started='2016-07-03')
        self.assertIsNotNone(read)
        self.assertIsNotNone(read.id)
        self.assertEquals(1, edition.reads.count())

        functions.edition.read.edit(edition, read.id, 'started', '2016-07-05')
        self.assertIsNotNone('2016-07-05', str(read.started))

        functions.edition.read.edit(edition, read.id, 'finished', '2016-07-15')
        self.assertIsNotNone('2016-07-15', str(read.finished))

        functions.edition.read.delete(edition, read.id)
        self.assertEquals(edition.reads.count(), 0)
