# -*- coding: utf-8 -*-
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


class LinkModelTestCase(TestCase):
    def test_from_to_dict(self):
        link, created = Link.objects.get_or_create(link="https://example.com")
        self.assertTrue(created)
        self.assertIsNotNone(link.id)
        self.assertEquals({"url": "https://example.com"}, link.to_dict())
        self.assertEquals((link, False), Link.from_dict({"url": "https://example.com"}))

    def test_edit(self):
        link, created = Link.objects.get_or_create(link="https://example.com")
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        link.edit("url", "https://example.de")
        self.assertEquals("https://example.de", link.link)

        link.edit("link", "https://example.org")
        self.assertEquals("https://example.org", link.link)

    def test_delete(self):
        link, created = Link.from_dict({"url": "https://example.com"})
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        link.delete()
        self.assertIsNone(link.id)

    def test_get(self):
        link, created = Link.from_dict({"url": "https://example.com"})
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        link2 = Link.get("https://example.com")
        self.assertIsNotNone(link2)
        self.assertEquals(link, link2)

        link2 = Link.get("example")
        self.assertIsNotNone(link2)
        self.assertEquals(link, link2)

        link2 = Link.get(str(link.id))
        self.assertIsNotNone(link2)
        self.assertEquals(link, link2)

    def test_search(self):
        link, created = Link.from_dict({"url": "https://example.com"})
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        link, created = Link.from_dict({"url": "http://test.org"})
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        link, created = Link.from_dict({"url": "https://example.org"})
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        links = Link.objects.all()
        self.assertEquals(3, len(links))

        links = Link.search("example")
        self.assertEquals(2, len(links))

        links = Link.search(".org")
        self.assertEquals(2, len(links))

    def test_print(self):
        link, created = Link.from_dict({"url": "https://example.com"})
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        with StringIO() as cout:
            link.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "URL                              https://example.com                "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

    def test_save(self):
        link = Link(link="https://example.com")
        link.save()
        self.assertIsNotNone(link.id)
