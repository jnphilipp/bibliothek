# -*- coding: utf-8 -*-

from django.test import TestCase
from publishers import functions


class PublisherFunctionsTestCase(TestCase):
    def test_publisher_create(self):
        publisher, created = functions.publisher.create('Test Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)


    def test_publisher_edit(self):
        publisher, created = functions.publisher.create('Test2 Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        functions.publisher.edit(publisher, 'name', 'IEEE Test Publisher')
        self.assertEquals(publisher.name, 'IEEE Test Publisher')


    def test_publisher_get(self):
        publisher, created = functions.publisher.create('Test Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publisher2 = functions.publisher.get.by_term('Test Publisher')
        self.assertIsNotNone(publisher)
        self.assertEquals(publisher, publisher2)


    def test_publisher_list(self):
        publisher, created = functions.publisher.create('Test Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publisher, created = functions.publisher.create('Test2 Publisher')
        self.assertTrue(created)
        self.assertIsNotNone(publisher.id)

        publishers = functions.publisher.list.all()
        self.assertEquals(len(publishers), 2)
