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
from magazines.functions import magazine as fmagazine, issue as fissue


class IssueFunctionsTestCase(TestCase):
    def setUp(self):
        self.magazine, created = fmagazine.create('Weekly')
        self.assertTrue(created)
        self.assertIsNotNone(self.magazine.id)


    def test_issue_create(self):
        issue, created = fissue.create(self.magazine, '1/2016',
                                       publishing_date='2016-01-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issue, created = fissue.create(self.magazine, '2/2016',
                                       publishing_date='2016-02-01',
                                       languages=['Deutsch'],
                                       links=['https://weekly.de/2-2016/'])
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)
        self.assertEquals(1, issue.languages.count())
        self.assertEquals('Deutsch', issue.languages.first().name)
        self.assertEquals(1, issue.links.count())
        self.assertEquals('https://weekly.de/2-2016/',
                          issue.links.first().link)


    def test_issue_edit(self):
        issue, created = fissue.create(self.magazine, '3/2016',
                                       publishing_date='2016-02-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        fissue.edit(issue, 'issue', '2/2016')
        self.assertEquals('2/2016', issue.issue)

        fissue.edit(issue, 'publishing_date', '2016-02-03')
        self.assertEquals('2016-02-03', issue.publishing_date)

        fissue.edit(issue, 'language', 'Deutsch')
        self.assertEquals(1, issue.languages.count())
        self.assertEquals('Deutsch', issue.languages.first().name)

        fissue.edit(issue, 'language', 'Espanol')
        self.assertEquals(2, issue.languages.count())
        self.assertEquals('Espanol', issue.languages.last().name)

        fissue.edit(issue, 'language', 'Deutsch')
        self.assertEquals(1, issue.languages.count())
        self.assertEquals('Espanol', issue.languages.first().name)

        fissue.edit(issue, 'link', 'https://weekly.de/3-2016/')
        self.assertEquals(1, issue.links.count())
        self.assertEquals('https://weekly.de/3-2016/',
                          issue.links.first().link)

        fissue.edit(issue, 'link', 'https://weekly.de/issue/3-2016')
        self.assertEquals(2, issue.links.count())
        self.assertEquals('https://weekly.de/issue/3-2016',
                          issue.links.last().link)

        fissue.edit(issue, 'link', 'https://weekly.de/3-2016/')
        self.assertEquals(1, issue.links.count())
        self.assertEquals('https://weekly.de/issue/3-2016',
                          issue.links.first().link)

    def test_issue_get(self):
        issue, created = fissue.create(self.magazine, '3/2016',
                                       publishing_date='2016-03-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issue2 = fissue.get.by_term(self.magazine, '3/2016')
        self.assertIsNotNone(issue)
        self.assertEquals(issue, issue2)

        issue2 = fissue.get.by_term(self.magazine, str(issue.id))
        self.assertIsNotNone(issue)
        self.assertEquals(issue, issue2)

    def test_issue_list(self):
        issue, created = fissue.create(self.magazine, '4/2016',
                                       publishing_date='2016-04-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issue, created = fissue.create(self.magazine, '5/2016',
                                       publishing_date='2016-05-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issues = fissue.list.all(self.magazine)
        self.assertEquals(2, len(issues))

        issues = fissue.list.by_term(self.magazine, '5/2016')
        self.assertEquals(1, len(issues))

    def test_issue_acquisition(self):
        issue, created = fissue.create(self.magazine, '6/2016',
                                       publishing_date='2016-06-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        acquisition = fissue.acquisition.add(issue, date='2016-06-02',
                                             price=2.5)
        self.assertIsNotNone(acquisition)
        self.assertEquals(1, issue.acquisitions.count())

        fissue.acquisition.edit(issue, acquisition.id, 'price', 5.75)
        self.assertIsNotNone(5.75, acquisition.price)

        fissue.acquisition.delete(issue, acquisition.id)
        self.assertEquals(0, issue.acquisitions.count())

    def test_issue_read(self):
        issue, created = fissue.create(self.magazine, '7/2016',
                                       publishing_date='2016-07-01')
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        read = fissue.read.add(issue, started='2016-07-03')
        self.assertIsNotNone(read)
        self.assertEquals(1, issue.reads.count())

        fissue.read.edit(issue, read.id, 'started', '2016-07-06')
        self.assertIsNotNone('2016-07-06', str(read.started))

        fissue.read.edit(issue, read.id, 'finished', '2016-07-15')
        self.assertIsNotNone('2016-07-15', str(read.finished))

        fissue.read.delete(issue, read.id)
        self.assertEquals(0, issue.reads.count())
