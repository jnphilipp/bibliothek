# -*- coding: utf-8 -*-

from django.test import TestCase
from magazines import functions


class IssueFunctionsTestCase(TestCase):
    def setUp(self):
        self.magazine, created = functions.magazine.create('Weekly')
        self.assertTrue(created)
        self.assertIsNotNone(self.magazine.id)


    def test_issue_create(self):
        issue, created = functions.issue.create(self.magazine, '1/2016', published_on='2016-01-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)


    def test_issue_edit(self):
        issue, created = functions.issue.create(self.magazine, '3/2016', published_on='2016-02-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        functions.issue.edit(issue, 'issue', '2/2016')
        self.assertEquals(issue.issue, '2/2016')


    def test_issue_get(self):
        issue, created = functions.issue.create(self.magazine, '3/2016', published_on='2016-03-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issue2 = functions.issue.get.by_term(self.magazine, '3/2016')
        self.assertIsNotNone(issue)
        self.assertEquals(issue, issue2)


    def test_issue_list(self):
        issue, created = functions.issue.create(self.magazine, '4/2016', published_on='2016-04-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issue, created = functions.issue.create(self.magazine, '5/2016', published_on='2016-05-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issues = functions.issue.list.all(self.magazine)
        self.assertEquals(len(issues), 2)

        issues = functions.issue.list.by_term(self.magazine, '5/2016')
        self.assertEquals(len(issues), 1)


    def test_issue_acquisition(self):
        issue, created = functions.issue.create(self.magazine, '6/2016', published_on='2016-06-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        acquisition = functions.issue.acquisition.add(issue, date='2016-06-02', price=2.5)
        self.assertIsNotNone(acquisition)
        self.assertEquals(issue.acquisitions.count(), 1)

        functions.issue.acquisition.edit(issue, acquisition.id, 'price', 5.75)
        self.assertIsNotNone(acquisition.price, 5.75)


        functions.issue.acquisition.delete(issue, acquisition.id)
        self.assertEquals(issue.acquisitions.count(), 0)


    def test_issue_read(self):
        issue, created = functions.issue.create(self.magazine, '7/2016', published_on='2016-07-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        read = functions.issue.read.add(issue, started='2016-07-03')
        self.assertIsNotNone(read)
        self.assertEquals(issue.reads.count(), 1)

        functions.issue.read.edit(issue, read.id, 'finished', '2016-07-15')
        self.assertIsNotNone(str(read.finished), '2016-07-15')


        functions.issue.read.delete(issue, read.id)
        self.assertEquals(issue.reads.count(), 0)
