# -*- coding: utf-8 -*-

from django.test import TestCase
from publishers import functions


class PublisherFunctionsTestCase(TestCase):
    def test_publisher_create(self):
        publisher, created = functions.publisher.create('Test Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publisher, created = functions.publisher.create('Test Press', links=['https://press.com'])
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)
        self.assertEquals(1, publisher.links.count())


    def test_publisher_edit(self):
        publisher, created = functions.publisher.create('Test2 Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        functions.publisher.edit(publisher, 'name', 'IEEE Test Publisher')
        self.assertEquals('IEEE Test Publisher', publisher.name)


    def test_publisher_get(self):
        publisher, created = functions.publisher.create('Test Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publisher2 = functions.publisher.get.by_term('Test Publisher')
        self.assertIsNotNone(publisher2)
        self.assertEquals(publisher, publisher2)

        publisher2 = functions.publisher.get.by_term(str(publisher.id))
        self.assertIsNotNone(publisher2)
        self.assertEquals(publisher, publisher2)


    def test_publisher_list(self):
        publisher, created = functions.publisher.create('Test Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publisher, created = functions.publisher.create('Test2 Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publisher, created = functions.publisher.create('Test Prees')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publishers = functions.publisher.list.all()
        self.assertEquals(3, len(publishers))

        publishers = functions.publisher.list.by_term('est P')
        self.assertEquals(2, len(publishers))
