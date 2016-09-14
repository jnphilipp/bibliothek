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

        issue, created = functions.issue.create(self.magazine, '2/2016', published_on='2016-02-01', languages=['Deutsch'], links=['https://weekly.de/2-2016/'])
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)
        self.assertEquals(1, issue.languages.count())
        self.assertEquals('Deutsch', issue.languages.first().name)
        self.assertEquals(1, issue.links.count())
        self.assertEquals('https://weekly.de/2-2016/', issue.links.first().link)


    def test_issue_edit(self):
        issue, created = functions.issue.create(self.magazine, '3/2016', published_on='2016-02-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        functions.issue.edit(issue, 'issue', '2/2016')
        self.assertEquals('2/2016', issue.issue)

        functions.issue.edit(issue, 'published_on', '2016-02-03')
        self.assertEquals('2016-02-03', issue.published_on)

        functions.issue.edit(issue, '+language', 'Deutsch')
        self.assertEquals(1, issue.languages.count())
        self.assertEquals('Deutsch', issue.languages.first().name)

        functions.issue.edit(issue, '+language', 'Espanol')
        self.assertEquals(2, issue.languages.count())
        self.assertEquals('Espanol', issue.languages.last().name)

        functions.issue.edit(issue, '-language', 'Deutsch')
        self.assertEquals(1, issue.languages.count())
        self.assertEquals('Espanol', issue.languages.first().name)

        functions.issue.edit(issue, '+link', 'https://weekly.de/3-2016/')
        self.assertEquals(1, issue.links.count())
        self.assertEquals('https://weekly.de/3-2016/', issue.links.first().link)

        functions.issue.edit(issue, '+link', 'https://weekly.de/issue/3-2016')
        self.assertEquals(2, issue.links.count())
        self.assertEquals('https://weekly.de/issue/3-2016', issue.links.last().link)

        functions.issue.edit(issue, '-link', 'https://weekly.de/3-2016/')
        self.assertEquals(1, issue.links.count())
        self.assertEquals('https://weekly.de/issue/3-2016', issue.links.first().link)


    def test_issue_get(self):
        issue, created = functions.issue.create(self.magazine, '3/2016', published_on='2016-03-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issue2 = functions.issue.get.by_term(self.magazine, '3/2016')
        self.assertIsNotNone(issue)
        self.assertEquals(issue, issue2)

        issue2 = functions.issue.get.by_term(self.magazine, str(issue.id))
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
        self.assertEquals(2, len(issues))

        issues = functions.issue.list.by_term(self.magazine, '5/2016')
        self.assertEquals(1, len(issues))


    def test_issue_acquisition(self):
        issue, created = functions.issue.create(self.magazine, '6/2016', published_on='2016-06-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        acquisition = functions.issue.acquisition.add(issue, date='2016-06-02', price=2.5)
        self.assertIsNotNone(acquisition)
        self.assertEquals(1, issue.acquisitions.count())

        functions.issue.acquisition.edit(issue, acquisition.id, 'price', 5.75)
        self.assertIsNotNone(5.75, acquisition.price)

        functions.issue.acquisition.delete(issue, acquisition.id)
        self.assertEquals(0, issue.acquisitions.count())


    def test_issue_read(self):
        issue, created = functions.issue.create(self.magazine, '7/2016', published_on='2016-07-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        read = functions.issue.read.add(issue, started='2016-07-03')
        self.assertIsNotNone(read)
        self.assertEquals(1, issue.reads.count())

        functions.issue.read.edit(issue, read.id, 'started', '2016-07-06')
        self.assertIsNotNone('2016-07-06', str(read.started))

        functions.issue.read.edit(issue, read.id, 'finished', '2016-07-15')
        self.assertIsNotNone('2016-07-15', str(read.finished))

        functions.issue.read.delete(issue, read.id)
        self.assertEquals(0, issue.reads.count())
