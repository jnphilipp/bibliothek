# -*- coding: utf-8 -*-

from django.test import TestCase
from links.models import Link
from magazines import functions


class MagazineFunctionsTestCase(TestCase):
    def test_magazine_create(self):
        magazine, created = functions.magazine.create('Weekly')
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        magazine, created = functions.magazine.create('Science Weekly', 'https://sw.com/feed/', ['https://sw.com'])
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)
        self.assertIsNotNone(magazine.feed)
        self.assertIsNotNone(magazine.feed.id)
        self.assertIsNotNone(1, magazine.links.count())


    def test_magazine_edit(self):
        magazine, created = functions.magazine.create('Monthly')
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        functions.magazine.edit(magazine, 'name', 'Monthlys')
        self.assertEquals('Monthlys', magazine.name)

        link = Link.objects.create(link='https://monthlys.com/feed/')
        self.assertIsNotNone(link.id)

        functions.magazine.edit(magazine, 'feed', str(link.id))
        self.assertEquals(link, magazine.feed)

        functions.magazine.edit(magazine, 'feed', 'https://monthlys.com/issues/feed/')
        self.assertEquals('https://monthlys.com/issues/feed/', magazine.feed.link)


    def test_magazine_get(self):
        magazine, created = functions.magazine.create('Weekly')
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        magazine2 = functions.magazine.get.by_term('Weekly')
        self.assertIsNotNone(magazine)
        self.assertEquals(magazine, magazine2)

        magazine2 = functions.magazine.get.by_term(str(magazine.id))
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
