# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2016-2022 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
from persons.models import Person


class PersonModelTestCase(TestCase):
    def test_from_to_dict(self):
        link, created = Link.objects.get_or_create(link="https://hans-mueller.de")
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        person, created = Person.objects.get_or_create(name="Hans Müller")
        person.links.add(link)
        self.assertTrue(created)
        self.assertIsNotNone(person.id)
        self.assertEquals(
            {"name": "Hans Müller", "links": [{"url": "https://hans-mueller.de"}]},
            person.to_dict(),
        )
        self.assertEquals(
            (person, False),
            Person.from_dict(
                {"name": "Hans Müller", "links": [{"url": "https://hans-mueller.de"}]}
            ),
        )
        self.assertEquals((person, False), Person.from_dict({"name": "Hans Müller"}))

        person, created = Person.objects.get_or_create(name="Jane Bond")
        self.assertTrue(created)
        self.assertIsNotNone(person.id)
        self.assertEquals({"name": "Jane Bond", "links": None}, person.to_dict())
        self.assertEquals(
            (person, False), Person.from_dict({"name": "Jane Bond", "links": None})
        )
        self.assertEquals((person, False), Person.from_dict({"name": "Jane Bond"}))

    def test_edit(self):
        person, created = Person.objects.get_or_create(name="Hans Müller")
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        person.edit("name", "Dr. Hans Müller")
        self.assertEquals("Dr. Hans Müller", person.name)

        self.assertEquals(0, person.links.count())
        person.edit("link", "https://hans-mueller.de")
        self.assertEquals(1, person.links.count())

    def test_delete(self):
        person, created = Person.from_dict({"name": "Hans Müller"})
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        deleted = person.delete()
        self.assertIsNone(person.id)
        self.assertEquals((1, {"persons.Person": 1}), deleted)

        person, created = Person.from_dict(
            {"name": "Hans Müller", "links": [{"url": "https://hans-mueller.de"}]}
        )
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        deleted = person.delete()
        self.assertIsNone(person.id)
        self.assertEquals(
            (3, {"persons.Person": 1, "persons.Person_links": 1, "links.Link": 1}),
            deleted,
        )

    def test_get(self):
        person, created = Person.from_dict({"name": "Hans Müller"})
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        person2 = Person.get("Hans Müller")
        self.assertIsNotNone(person2)
        self.assertEquals(person, person2)

        person2 = Person.get("müller")
        self.assertIsNotNone(person2)
        self.assertEquals(person, person2)

        person2 = Person.get(str(person.id))
        self.assertIsNotNone(person2)
        self.assertEquals(person, person2)

    def test_get_or_create(self):
        person, created = Person.from_dict({"name": "Hans Müller"})
        self.assertTrue(created)
        self.assertIsNotNone(person.id)
        self.assertEquals(1, Person.objects.count())

        person2 = Person.get_or_create("Hans Müller")
        self.assertIsNotNone(person2)
        self.assertEquals(person, person2)
        self.assertEquals(1, Person.objects.count())

        person2 = Person.get_or_create(str(person.id))
        self.assertIsNotNone(person2)
        self.assertEquals(person, person2)
        self.assertEquals(1, Person.objects.count())

        person2 = Person.get_or_create("Franz Müller")
        self.assertIsNotNone(person2)
        self.assertNotEquals(person, person2)
        self.assertEquals(2, Person.objects.count())

    def test_search(self):
        person, created = Person.from_dict({"name": "Hans Müller"})
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        person, created = Person.from_dict({"name": "Maria Müller"})
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        person, created = Person.from_dict({"name": "Maria Vogel"})
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        self.assertEquals(3, Person.objects.all().count())
        self.assertEquals(2, Person.search("Maria").count())
        self.assertEquals(2, Person.search("müller").count())

    def test_print(self):
        person, created = Person.from_dict({"name": "Hans Müller"})
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        with StringIO() as cout:
            person.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Name                             Hans Müller                        "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Links                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Books                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Editions                                                            "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Papers                                                              "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

    def test_save(self):
        person = Person(name="Hans Müller")
        person.save()
        self.assertIsNotNone(person.id)
        self.assertEquals("hans-muller", person.slug)

        person = Person(name="J. T. Do")
        person.save()
        self.assertIsNotNone(person.id)
        self.assertEquals("j-t-do", person.slug)
