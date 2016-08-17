# -*- coding: utf-8 -*-

from django.test import TestCase
from magazines import functions


class MagazineFunctionsTestCase(TestCase):
    def test_magazine_create(self):
        magazine, created = functions.magazine.create('Weekly')
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)


    def test_magazine_edit(self):
        magazine, created = functions.magazine.create('Monthly')
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        functions.magazine.edit(magazine, 'name', 'Monthlys')
        self.assertEquals(magazine.name, 'Monthlys')


    def test_magazine_get(self):
        magazine, created = functions.magazine.create('Weekly')
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        magazine2 = functions.magazine.get.by_term('Weekly')
        self.assertIsNotNone(magazine)
        self.assertEquals(magazine, magazine2)


    def test_magazine_list(self):
        magazine, created = functions.magazine.create('Weekly')
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        magazine, created = functions.magazine.create('Monthly')
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        magazines = functions.magazine.list.all()
        self.assertEquals(len(magazines), 2)

        magazines = functions.magazine.list.by_term('Monthly')
        self.assertEquals(len(magazines), 1)
