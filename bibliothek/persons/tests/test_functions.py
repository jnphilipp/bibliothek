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
from persons import functions


class PersonFunctionsTestCase(TestCase):
    def test_person_create(self):
        person, created = functions.person.create('Hans', 'Müller')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        person2, created = functions.person.create('Jan', 'Müller',
                                                   links=['https://jan.de'])
        self.assertTrue(created)
        self.assertIsNotNone(person2.id)
        self.assertEquals(1, person2.links.count())

    def test_person_edit(self):
        person, created = functions.person.create('Frank', 'Schmidt')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        functions.person.edit(person, 'last_name', 'Schmidts')
        self.assertEquals('Schmidts', person.last_name)

        functions.person.edit(person, 'first_name', 'Franky')
        self.assertEquals('Franky', person.first_name)

    def test_person_get(self):
        person, created = functions.person.create('Karl', 'Heinz')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        person2 = functions.person.get.by_term('rl Hei')
        self.assertIsNotNone(person2)
        self.assertEquals(person, person2)

        person2 = functions.person.get.by_term(str(person.id))
        self.assertIsNotNone(person2)
        self.assertEquals(person, person2)

    def test_person_list(self):
        person, created = functions.person.create('Anne', 'Karenina')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        person, created = functions.person.create('Sarah', 'Vogel')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        person, created = functions.person.create('Karen', 'Stirling')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        persons = functions.person.list.all()
        self.assertEquals(3, len(persons))

        persons = functions.person.list.by_term('Karen')
        self.assertEquals(2, len(persons))
