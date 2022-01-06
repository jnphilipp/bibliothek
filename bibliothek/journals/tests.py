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
from journals.models import Journal
from links.models import Link


class JournalModelTestCase(TestCase):
    def test_from_to_dict(self):
        link, created = Link.objects.get_or_create(link="https://tj.org")
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        journal, created = Journal.objects.get_or_create(name="Test Journal")
        journal.links.add(link)
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)
        self.assertEquals(
            {"name": "Test Journal", "links": [{"url": "https://tj.org"}]},
            journal.to_dict(),
        )
        self.assertEquals(
            (journal, False),
            Journal.from_dict(
                {"name": "Test Journal", "links": [{"url": "https://tj.org"}]}
            ),
        )
        self.assertEquals((journal, False), Journal.from_dict({"name": "Test Journal"}))

        journal, created = Journal.objects.get_or_create(name="Random Journal")
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)
        self.assertEquals({"name": "Random Journal", "links": None}, journal.to_dict())
        self.assertEquals(
            (journal, False),
            Journal.from_dict({"name": "Random Journal", "links": None}),
        )
        self.assertEquals(
            (journal, False), Journal.from_dict({"name": "Random Journal"})
        )

    def test_delete(self):
        journals, created = Journal.from_dict({"name": "Science Journal"})
        self.assertTrue(created)
        self.assertIsNotNone(journals.id)

        deleted = journals.delete()
        self.assertIsNone(journals.id)
        self.assertEquals((1, {"journals.Journal": 1}), deleted)

        journals, created = Journal.from_dict(
            {"name": "Nature Science Journal", "links": [{"url": "https://nsj.org"}]}
        )
        self.assertTrue(created)
        self.assertIsNotNone(journals.id)

        deleted = journals.delete()
        self.assertIsNone(journals.id)
        self.assertEquals(
            (3, {"journals.Journal": 1, "journals.Journal_links": 1, "links.Link": 1}),
            deleted,
        )

    def test_edit(self):
        journal, created = Journal.objects.get_or_create(name="Science Journal")
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal.edit("name", "The Science Journal")
        self.assertEquals("The Science Journal", journal.name)

        self.assertEquals(0, journal.links.count())
        journal.edit("link", "https://tsj.net")
        self.assertEquals(1, journal.links.count())

    def test_get(self):
        journal, created = Journal.from_dict({"name": "Science Journal"})
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal2 = Journal.get("Science Journal")
        self.assertIsNotNone(journal2)
        self.assertEquals(journal, journal2)

        journal2 = Journal.get("science")
        self.assertIsNotNone(journal2)
        self.assertEquals(journal, journal2)

        journal2 = Journal.get(str(journal.id))
        self.assertIsNotNone(journal2)
        self.assertEquals(journal, journal2)

    def test_get_or_create(self):
        journal, created = Journal.from_dict({"name": "Science Journal"})
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)
        self.assertEquals(1, Journal.objects.count())

        journal2 = Journal.get_or_create("Science Journal")
        self.assertIsNotNone(journal2)
        self.assertEquals(journal, journal2)
        self.assertEquals(1, Journal.objects.count())

        journal2 = Journal.get_or_create(str(journal.id))
        self.assertIsNotNone(journal2)
        self.assertEquals(journal, journal2)
        self.assertEquals(1, Journal.objects.count())

        journal2 = Journal.get_or_create("IT Journal")
        self.assertIsNotNone(journal2)
        self.assertNotEquals(journal, journal2)
        self.assertEquals(2, Journal.objects.count())

    def test_search(self):
        journal, created = Journal.from_dict({"name": "Science Journal"})
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal, created = Journal.from_dict({"name": "Nature Journal"})
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal, created = Journal.from_dict({"name": "Math science"})
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        self.assertEquals(3, Journal.objects.all().count())
        self.assertEquals(2, Journal.search("journal").count())
        self.assertEquals(2, Journal.search("science").count())

    def test_print(self):
        journal, created = Journal.from_dict({"name": "Science Journal"})
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        with StringIO() as cout:
            journal.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Name                             Science Journal                    "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Links                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Papers                                                              "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

    def test_save(self):
        journal = Journal(name="Science Journal")
        journal.save()
        self.assertIsNotNone(journal.id)
        self.assertEquals("science-journal", journal.slug)

        journal = Journal(name="Random Math Journal")
        journal.save()
        self.assertIsNotNone(journal.id)
        self.assertEquals("random-math-journal", journal.slug)
