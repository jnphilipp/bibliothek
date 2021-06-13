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
from publishers.models import Publisher


class PublisherModelTestCase(TestCase):
    def test_from_to_dict(self):
        link, created = Link.objects.get_or_create(link="https://press.org")
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        publisher, created = Publisher.objects.get_or_create(name="Test Press")
        publisher.links.add(link)
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)
        self.assertEquals(
            {"name": "Test Press", "links": [{"url": "https://press.org"}]},
            publisher.to_dict(),
        )
        self.assertEquals(
            (publisher, False),
            Publisher.from_dict(
                {"name": "Test Press", "links": [{"url": "https://press.org"}]}
            ),
        )
        self.assertEquals(
            (publisher, False), Publisher.from_dict({"name": "Test Press"})
        )

        publisher, created = Publisher.objects.get_or_create(name="Random Press")
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)
        self.assertEquals({"name": "Random Press", "links": None}, publisher.to_dict())
        self.assertEquals(
            (publisher, False),
            Publisher.from_dict({"name": "Random Press", "links": None}),
        )
        self.assertEquals(
            (publisher, False), Publisher.from_dict({"name": "Random Press"})
        )

    def test_delete(self):
        publisher, created = Publisher.from_dict({"name": "Publishing House"})
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        deleted = publisher.delete()
        self.assertIsNone(publisher.id)
        self.assertEquals((1, {"publishers.Publisher": 1}), deleted)

        publisher, created = Publisher.from_dict(
            {"name": "Publishing House", "links": [{"url": "https://publishing.house"}]}
        )
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        deleted = publisher.delete()
        self.assertIsNone(publisher.id)
        self.assertEquals(
            (
                3,
                {
                    "publishers.Publisher": 1,
                    "publishers.Publisher_links": 1,
                    "links.Link": 1,
                },
            ),
            deleted,
        )

    def test_edit(self):
        publisher, created = Publisher.objects.get_or_create(name="Publishing House")
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publisher.edit("name", "The Publishing House")
        self.assertEquals("The Publishing House", publisher.name)

        self.assertEquals(0, publisher.links.count())
        publisher.edit("link", "https://publishing.house")
        self.assertEquals(1, publisher.links.count())

    def test_get(self):
        publisher, created = Publisher.from_dict({"name": "Publishing House"})
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publisher2 = Publisher.get("Publishing House")
        self.assertIsNotNone(publisher2)
        self.assertEquals(publisher, publisher2)

        publisher2 = Publisher.get("house")
        self.assertIsNotNone(publisher2)
        self.assertEquals(publisher, publisher2)

        publisher2 = Publisher.get(str(publisher.id))
        self.assertIsNotNone(publisher2)
        self.assertEquals(publisher, publisher2)

    def test_get_or_create(self):
        publisher, created = Publisher.from_dict({"name": "Publishing House"})
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)
        self.assertEquals(1, Publisher.objects.count())

        publisher2 = Publisher.get_or_create("Publishing House")
        self.assertIsNotNone(publisher2)
        self.assertEquals(publisher, publisher2)
        self.assertEquals(1, Publisher.objects.count())

        publisher2 = Publisher.get_or_create(str(publisher.id))
        self.assertIsNotNone(publisher2)
        self.assertEquals(publisher, publisher2)
        self.assertEquals(1, Publisher.objects.count())

        publisher2 = Publisher.get_or_create("Old House")
        self.assertIsNotNone(publisher2)
        self.assertNotEquals(publisher, publisher2)
        self.assertEquals(2, Publisher.objects.count())

    def test_search(self):
        publisher, created = Publisher.from_dict({"name": "Publishing House"})
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publisher, created = Publisher.from_dict({"name": "Old House"})
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publisher, created = Publisher.from_dict({"name": "Publishing Press"})
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        self.assertEquals(3, Publisher.objects.all().count())
        self.assertEquals(2, Publisher.search("pub").count())
        self.assertEquals(2, Publisher.search("House").count())

    def test_print(self):
        publisher, created = Publisher.from_dict({"name": "Publishing House"})
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        with StringIO() as cout:
            publisher.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Name                             Publishing House                   "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Links                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Editions                                                            "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

    def test_save(self):
        publisher = Publisher(name="Publishing House")
        publisher.save()
        self.assertIsNotNone(publisher.id)
        self.assertEquals("publishing-house", publisher.slug)

        publisher = Publisher(name="Random")
        publisher.save()
        self.assertIsNotNone(publisher.id)
        self.assertEquals("random", publisher.slug)
