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
from publishers.functions import publisher as fpublisher


class PublisherFunctionsTestCase(TestCase):
    def test_publisher_create(self):
        publisher, created = fpublisher.create('Test Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publisher, created = fpublisher.create('Test Press',
                                               links=['https://press.com'])
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)
        self.assertEquals(1, publisher.links.count())

    def test_publisher_edit(self):
        publisher, created = fpublisher.create('Test2 Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        fpublisher.edit(publisher, 'name', 'IEEE Test Publisher')
        self.assertEquals('IEEE Test Publisher', publisher.name)

        fpublisher.edit(publisher, 'link', 'https://example.com')
        self.assertEquals(1, publisher.links.count())
        self.assertEquals('https://example.com', publisher.links.first().link)

        fpublisher.edit(publisher, 'link', 'https://test-publisher.com')
        self.assertEquals(2, publisher.links.count())
        self.assertEquals('https://test-publisher.com',
                          publisher.links.last().link)

        fpublisher.edit(publisher, 'link', 'https://example.com')
        self.assertEquals(1, publisher.links.count())
        self.assertEquals('https://test-publisher.com',
                          publisher.links.first().link)

    def test_publisher_get(self):
        publisher, created = fpublisher.create('Test Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publisher2 = fpublisher.get.by_term('Test Publisher')
        self.assertIsNotNone(publisher2)
        self.assertEquals(publisher, publisher2)

        publisher2 = fpublisher.get.by_term(str(publisher.id))
        self.assertIsNotNone(publisher2)
        self.assertEquals(publisher, publisher2)

    def test_publisher_list(self):
        publisher, created = fpublisher.create('Test Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publisher, created = fpublisher.create('Test2 Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publisher, created = fpublisher.create('Test Prees')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publishers = fpublisher.list.all()
        self.assertEquals(3, len(publishers))

        publishers = fpublisher.list.by_term('est P')
        self.assertEquals(2, len(publishers))
