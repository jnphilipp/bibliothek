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
