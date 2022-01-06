# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2016-2021 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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

from genres.models import Genre
from django.test import TestCase
from io import StringIO


class GenreModelTestCase(TestCase):
    def test_from_to_dict(self):
        genre, created = Genre.objects.get_or_create(name="Fiction")
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)
        self.assertEquals({"name": "Fiction"}, genre.to_dict())
        self.assertEquals((genre, False), Genre.from_dict({"name": "Fiction"}))

    def test_edit(self):
        genre, created = Genre.objects.get_or_create(name="SciFi")
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)

        genre.edit("name", "Science Fiction")
        self.assertEquals("Science Fiction", genre.name)

    def test_delete(self):
        genre, created = Genre.from_dict({"name": "Fiction"})
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)

        deleted = genre.delete()
        self.assertIsNone(genre.id)
        self.assertEquals((1, {"genres.Genre": 1}), deleted)

    def test_get(self):
        genre, created = Genre.from_dict({"name": "Science Fiction"})
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)

        genre2 = Genre.get("Science Fiction")
        self.assertIsNotNone(genre2)
        self.assertEquals(genre, genre2)

        genre2 = Genre.get("fiction")
        self.assertIsNotNone(genre2)
        self.assertEquals(genre, genre2)

        genre2 = Genre.get(str(genre.id))
        self.assertIsNotNone(genre2)
        self.assertEquals(genre, genre2)

    def test_get_or_create(self):
        genre, created = Genre.from_dict({"name": "Science Fiction"})
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)
        self.assertEquals(1, Genre.objects.count())

        genre2 = Genre.get_or_create("Science Fiction")
        self.assertIsNotNone(genre2)
        self.assertEquals(genre, genre2)
        self.assertEquals(1, Genre.objects.count())

        genre2 = Genre.get_or_create(str(genre.id))
        self.assertIsNotNone(genre2)
        self.assertEquals(genre, genre2)
        self.assertEquals(1, Genre.objects.count())

        genre2 = Genre.get_or_create("SciFi")
        self.assertIsNotNone(genre2)
        self.assertNotEquals(genre, genre2)
        self.assertEquals(2, Genre.objects.count())

    def test_search(self):
        genre, created = Genre.from_dict({"name": "Science Fiction"})
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)

        genre, created = Genre.from_dict({"name": "Romance"})
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)

        genre, created = Genre.from_dict({"name": "Fiction"})
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)

        self.assertEquals(3, Genre.objects.all().count())
        self.assertEquals(2, Genre.search("fiction").count())
        self.assertEquals(2, Genre.search("ce").count())

    def test_print(self):
        genre, created = Genre.from_dict({"name": "Science Fiction"})
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)

        with StringIO() as cout:
            genre.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Name                             Science Fiction                    "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                "Books                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

    def test_save(self):
        genre = Genre(name="Science Fiction")
        genre.save()
        self.assertIsNotNone(genre.id)
        self.assertEquals("science-fiction", genre.slug)

        genre = Genre(name="Fiction")
        genre.save()
        self.assertIsNotNone(genre.id)
        self.assertEquals("fiction", genre.slug)
