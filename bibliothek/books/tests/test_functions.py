# -*- coding: utf-8 -*-

from books import functions
from django.test import TestCase
from persons import functions as pfunctions
from series import functions as sfunctions


class BookFunctionsTestCase(TestCase):
    def test_book_create(self):
        book, created = functions.book.create('Test Book')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        person, created = pfunctions.person.create('Firstname', 'Lastname')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        series, created = sfunctions.series.create('Test Series')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        book, created = functions.book.create('Some Test Book', [person.id], series.id, 1.0)
        self.assertTrue(created)
        self.assertIsNotNone(book.id)
        self.assertEquals(1, book.authors.count())
        self.assertEquals(person, book.authors.first())
        self.assertEquals(series, book.series)


    def test_book_edit(self):
        series, created = sfunctions.series.create('Test Series')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        book, created = functions.book.create('Test2 Book', series_id=series.id, volume=1.0)
        self.assertTrue(created)
        self.assertIsNotNone(book.id)
        self.assertEquals(series, book.series)

        functions.book.edit(book, 'title', 'IEEE Test Book')
        self.assertEquals('IEEE Test Book', book.title)

        series, created = sfunctions.series.create('Space Series')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        functions.book.edit(book, 'series', series.id)
        self.assertEquals(series, book.series)

        functions.book.edit(book, 'volume', 0.75)
        self.assertEquals(0.75, book.volume)


    def test_book_get(self):
        book, created = functions.book.create('Test Book')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        book2 = functions.book.get.by_term('Test Book')
        self.assertIsNotNone(book2)
        self.assertEquals(book, book2)

        book2 = functions.book.get.by_term(str(book.id))
        self.assertIsNotNone(book2)
        self.assertEquals(book, book2)


    def test_book_list(self):
        book, created = functions.book.create('About Stuff')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        book, created = functions.book.create('Not so cool Stuff')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        book, created = functions.book.create('About cool Stuff')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        books = functions.book.list.all()
        self.assertEquals(3, len(books))

        books = functions.book.list.by_term('cool Stuff')
        self.assertEquals(2, len(books))
