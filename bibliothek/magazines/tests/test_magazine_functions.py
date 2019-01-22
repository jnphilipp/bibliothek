# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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
from links.models import Link
from magazines.functions import magazine as fmagazine


class MagazineFunctionsTestCase(TestCase):
    def test_magazine_create(self):
        magazine, created = fmagazine.create('Weekly')
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        magazine, created = fmagazine.create('Science Weekly',
                                             'https://sw.com/feed/',
                                             ['https://sw.com'])
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)
        self.assertIsNotNone(magazine.feed)
        self.assertIsNotNone(magazine.feed.id)
        self.assertIsNotNone(1, magazine.links.count())

    def test_magazine_edit(self):
        magazine, created = fmagazine.create('Monthly')
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        fmagazine.edit(magazine, 'name', 'Monthlys')
        self.assertEquals('Monthlys', magazine.name)

        link = Link.objects.create(link='https://monthlys.com/feed/')
        self.assertIsNotNone(link.id)

        fmagazine.edit(magazine, 'feed', str(link.id))
        self.assertEquals(link, magazine.feed)

        fmagazine.edit(magazine, 'feed', 'https://monthlys.com/issues/feed/')
        self.assertEquals('https://monthlys.com/issues/feed/',
                          magazine.feed.link)

        fmagazine.edit(magazine, 'link', 'https://test.com')
        self.assertEquals(1, magazine.links.count())
        self.assertEquals('https://test.com', magazine.links.first().link)

        fmagazine.edit(magazine, 'link', 'https://test2.com')
        self.assertEquals(2, magazine.links.count())
        self.assertEquals('https://test2.com', magazine.links.last().link)

        fmagazine.edit(magazine, 'link', 'https://test.com')
        self.assertEquals(1, magazine.links.count())
        self.assertEquals('https://test2.com', magazine.links.first().link)

    def test_magazine_get(self):
        magazine, created = fmagazine.create('Weekly')
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        magazine2 = fmagazine.get.by_term('Weekly')
        self.assertIsNotNone(magazine)
        self.assertEquals(magazine, magazine2)

        magazine2 = fmagazine.get.by_term(str(magazine.id))
        self.assertIsNotNone(magazine)
        self.assertEquals(magazine, magazine2)

    def test_magazine_list(self):
        magazine, created = fmagazine.create('Weekly')
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        magazine, created = fmagazine.create('Monthly')
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        magazines = fmagazine.list.all()
        self.assertEquals(len(magazines), 2)

        magazines = fmagazine.list.by_term('Monthly')
        self.assertEquals(len(magazines), 1)
