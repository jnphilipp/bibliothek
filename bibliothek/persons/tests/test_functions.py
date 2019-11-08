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
from persons.functions import person as fperson


class PersonFunctionsTestCase(TestCase):
    def test_person_create(self):
        person, created = fperson.create('Hans Müller')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        person2, created = fperson.create('Jan Müller',
                                          links=['https://jan.de'])
        self.assertTrue(created)
        self.assertIsNotNone(person2.id)
        self.assertEquals(1, person2.links.count())

    def test_person_edit(self):
        person, created = fperson.create('Frank Schmidt')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        fperson.edit(person, 'name', 'Franky Schmidts')
        self.assertEquals('Franky Schmidts', person.name)

        fperson.edit(person, 'link', 'https://test.com')
        self.assertEquals(1, person.links.count())
        self.assertEquals('https://test.com', person.links.first().link)

        fperson.edit(person, 'link', 'https://example.com')
        self.assertEquals(2, person.links.count())
        self.assertEquals('https://example.com', person.links.first().link)

        fperson.edit(person, 'link', 'https://test.com')
        self.assertEquals(1, person.links.count())
        self.assertEquals('https://example.com', person.links.first().link)

    def test_person_get(self):
        person, created = fperson.create('Karl Heinz')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        person2 = fperson.get.by_term('rl Hei')
        self.assertIsNotNone(person2)
        self.assertEquals(person, person2)

        person2 = fperson.get.by_term(str(person.id))
        self.assertIsNotNone(person2)
        self.assertEquals(person, person2)

    def test_person_list(self):
        person, created = fperson.create('Anne Karenina')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        person, created = fperson.create('Sarah Vogel')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        person, created = fperson.create('Karen Stirling')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        persons = fperson.list.all()
        self.assertEquals(3, len(persons))

        persons = fperson.list.by_term('Karen')
        self.assertEquals(2, len(persons))
