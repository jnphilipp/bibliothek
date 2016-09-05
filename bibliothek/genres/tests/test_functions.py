# -*- coding: utf-8 -*-

from django.test import TestCase
from genres import functions


class GenreFunctionsTestCase(TestCase):
    def test_genre_create(self):
        genre, created = functions.genre.create('Fiction')
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)


    def test_genre_edit(self):
        genre, created = functions.genre.create('SciFi')
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)

        functions.genre.edit(genre, 'name', 'Science Fiction')
        self.assertEquals('Science Fiction', genre.name)


    def test_genre_get(self):
        genre, created = functions.genre.create('Fiction')
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)

        genre2 = functions.genre.get.by_term('Fiction')
        self.assertIsNotNone(genre2)
        self.assertEquals(genre, genre2)

        genre2 = functions.genre.get.by_term(str(genre.id))
        self.assertIsNotNone(genre2)
        self.assertEquals(genre, genre2)


    def test_genre_list(self):
        genre, created = functions.genre.create('Science Fiction')
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)

        genre, created = functions.genre.create('Romance')
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)

        genre, created = functions.genre.create('Fiction')
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)

        genres = functions.genre.list.all()
        self.assertEquals(3, len(genres))

        genres = functions.genre.list.by_term('Fiction')
        self.assertEquals(2, len(genres))
