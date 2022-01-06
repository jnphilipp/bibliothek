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

from django.test import TestCase
from io import StringIO
from links.models import Link
from series.models import Series


class SeriesModelTestCase(TestCase):
    def test_from_to_dict(self):
        link, created = Link.objects.get_or_create(link="https://secrectfiles.com")
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        series, created = Series.objects.get_or_create(name="Secret Files")
        series.links.add(link)
        self.assertTrue(created)
        self.assertIsNotNone(series.id)
        self.assertEquals(
            {"name": "Secret Files", "links": [{"url": "https://secrectfiles.com"}]},
            series.to_dict(),
        )
        self.assertEquals(
            (series, False),
            Series.from_dict(
                {"name": "Secret Files", "links": [{"url": "https://secrectfiles.com"}]}
            ),
        )
        self.assertEquals((series, False), Series.from_dict({"name": "Secret Files"}))

        series, created = Series.objects.get_or_create(name="Random")
        self.assertTrue(created)
        self.assertIsNotNone(series.id)
        self.assertEquals({"name": "Random", "links": None}, series.to_dict())
        self.assertEquals(
            (series, False), Series.from_dict({"name": "Random", "links": None})
        )
        self.assertEquals((series, False), Series.from_dict({"name": "Random"}))

    def test_delete(self):
        series, created = Series.from_dict({"name": "Secret Files"})
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        deleted = series.delete()
        self.assertIsNone(series.id)
        self.assertEquals((1, {"series.Series": 1}), deleted)

        series, created = Series.from_dict(
            {"name": "Secret Files", "links": [{"url": "https://secrectfiles.com"}]}
        )
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        deleted = series.delete()
        self.assertIsNone(series.id)
        self.assertEquals(
            (3, {"series.Series": 1, "series.Series_links": 1, "links.Link": 1}),
            deleted,
        )

    def test_edit(self):
        series, created = Series.objects.get_or_create(name="Secret Files")
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        series.edit("name", "The Secret Files")
        self.assertEquals("The Secret Files", series.name)

        self.assertEquals(0, series.links.count())
        series.edit("link", "https://the-secret-files.com")
        self.assertEquals(1, series.links.count())

    def test_get(self):
        series, created = Series.from_dict({"name": "Secret Files"})
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        series2 = Series.get("Secret Files")
        self.assertIsNotNone(series2)
        self.assertEquals(series, series2)

        series2 = Series.get("files")
        self.assertIsNotNone(series2)
        self.assertEquals(series, series2)

        series2 = Series.get(str(series.id))
        self.assertIsNotNone(series2)
        self.assertEquals(series, series2)

    def test_get_or_create(self):
        series, created = Series.from_dict({"name": "Secret Files"})
        self.assertTrue(created)
        self.assertIsNotNone(series.id)
        self.assertEquals(1, Series.objects.count())

        series2 = Series.get_or_create("Secret Files")
        self.assertIsNotNone(series2)
        self.assertEquals(series, series2)
        self.assertEquals(1, Series.objects.count())

        series2 = Series.get_or_create(str(series.id))
        self.assertIsNotNone(series2)
        self.assertEquals(series, series2)
        self.assertEquals(1, Series.objects.count())

        series2 = Series.get_or_create("Secret Papers")
        self.assertIsNotNone(series2)
        self.assertNotEquals(series, series2)
        self.assertEquals(2, Series.objects.count())

    def test_search(self):
        series, created = Series.from_dict({"name": "Secret Files"})
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        series, created = Series.from_dict({"name": "Ran"})
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        series, created = Series.from_dict({"name": "Random Files"})
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        self.assertEquals(3, Series.objects.all().count())
        self.assertEquals(2, Series.search("files").count())
        self.assertEquals(2, Series.search("ran").count())

    def test_print(self):
        series, created = Series.from_dict({"name": "Secret Files"})
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        with StringIO() as cout:
            series.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Name                             Secret Files                       "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Links                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Books                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

    def test_save(self):
        series = Series(name="Some Series")
        series.save()
        self.assertIsNotNone(series.id)
        self.assertEquals("some-series", series.slug)

        series = Series(name="Deep Space")
        series.save()
        self.assertIsNotNone(series.id)
        self.assertEquals("deep-space", series.slug)
