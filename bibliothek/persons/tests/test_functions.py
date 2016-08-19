# -*- coding: utf-8 -*-

from django.test import TestCase
from persons import functions


class PersonFunctionsTestCase(TestCase):
    def test_person_create(self):
        person, created = functions.person.create('Hans', 'Müller')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        person2, created = functions.person.create('Jan', 'Müller', links=['https://jan.de'])
        self.assertTrue(created)
        self.assertIsNotNone(person2.id)
        self.assertEquals(1, person2.links.count())


    def test_person_edit(self):
        person, created = functions.person.create('Frank', 'Schmidt')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        functions.person.edit(person, 'last_name', 'Schmidts')
        self.assertEquals(person.last_name, 'Schmidts')

        functions.person.edit(person, 'first_name', 'Franky')
        self.assertEquals(person.first_name, 'Franky')


    def test_person_get(self):
        person, created = functions.person.create('Karl', 'Heinz')
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        person2 = functions.person.get.by_term('rl Hei')
        self.assertIsNotNone(person)
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
