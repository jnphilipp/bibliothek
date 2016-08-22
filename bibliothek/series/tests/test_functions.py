# -*- coding: utf-8 -*-

from django.test import TestCase
from series import functions


class SeriesFunctionsTestCase(TestCase):
    def test_publisher_create(self):
        series, created = functions.series.create('Some Series')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)


    def test_series_edit(self):
        series, created = functions.series.create('Some other Series')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        functions.series.edit(series, 'name', 'Some cool Series')
        self.assertEquals('Some cool Series', series.name)


    def test_series_get(self):
        series, created = functions.series.create('Space Series')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        series2 = functions.series.get.by_term('Space Series')
        self.assertIsNotNone(series)
        self.assertEquals(series, series2)

        series2 = functions.series.get.by_term(str(series.id))
        self.assertIsNotNone(series)
        self.assertEquals(series, series2)


    def test_series_list(self):
        series, created = functions.series.create('Space')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        series, created = functions.series.create('Deep Space')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        series, created = functions.series.create('Home')
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        series = functions.series.list.all()
        self.assertEquals(3, len(series))

        series = functions.series.list.by_term('Space')
        self.assertEquals(2, len(series))
