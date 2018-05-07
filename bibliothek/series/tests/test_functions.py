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
from series.functions import series as fseries


class SeriesFunctionsTestCase(TestCase):
    def test_publisher_create(self):
        series, created = fseries.create('Some Series')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        series, created = fseries.create('Secret Files',
                                         links=['https://secrectfiles.com'])
        self.assertTrue(created)
        self.assertIsNotNone(series.id)
        self.assertEquals(1, series.links.count())
        self.assertEquals('https://secrectfiles.com',
                          series.links.first().link)

    def test_series_edit(self):
        series, created = fseries.create('Some other Series')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        fseries.edit(series, 'name', 'Some cool Series')
        self.assertEquals('Some cool Series', series.name)

        fseries.edit(series, 'link', 'https://test.com')
        self.assertEquals(1, series.links.count())
        self.assertEquals('https://test.com', series.links.first().link)

        fseries.edit(series, 'link', 'https://testsome.com')
        self.assertEquals(2, series.links.count())
        self.assertEquals('https://testsome.com', series.links.last().link)

        fseries.edit(series, 'link', 'https://test.com')
        self.assertEquals(1, series.links.count())
        self.assertEquals('https://testsome.com', series.links.first().link)

    def test_series_get(self):
        series, created = fseries.create('Space Series')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        series2 = fseries.get.by_term('Space Series')
        self.assertIsNotNone(series)
        self.assertEquals(series, series2)

        series2 = fseries.get.by_term(str(series.id))
        self.assertIsNotNone(series)
        self.assertEquals(series, series2)

    def test_series_list(self):
        series, created = fseries.create('Space')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        series, created = fseries.create('Deep Space')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        series, created = fseries.create('Home')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        series = fseries.list.all()
        self.assertEquals(3, len(series))

        series = fseries.list.by_term('Space')
        self.assertEquals(2, len(series))
