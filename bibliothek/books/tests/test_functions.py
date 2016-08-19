# -*- coding: utf-8 -*-

from django.test import TestCase
from books import functions


class BookFunctionsTestCase(TestCase):
    def test_book_create(self):
        book, created = functions.book.create('Test Book')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)


    def test_book_edit(self):
        book, created = functions.book.create('Test2 Book')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        functions.book.edit(book, 'title', 'IEEE Test Book')
        self.assertEquals(book.title, 'IEEE Test Book')


    def test_book_get(self):
        book, created = functions.book.create('Test Book')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        book2 = functions.book.get.by_term('Test Book')
        self.assertIsNotNone(book)
        self.assertEquals(book, book2)


    def test_book_list(self):
        book, created = functions.book.create('Test Book')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        book, created = functions.book.create('Test2 Book')
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        books = functions.book.list.all()
        self.assertEquals(len(books), 2)
