# -*- coding: utf-8 -*-

from django.test import TestCase
from papers import functions


class PaperFunctionsTestCase(TestCase):
    def test_paper_create(self):
        paper, created = functions.paper.create('Paper')
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)


    def test_paper_edit(self):
        paper, created = functions.paper.create('Paper 2')
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        functions.paper.edit(paper, 'title', 'Paper Two')
        self.assertEquals(paper.title, 'Paper Two')


    def test_paper_get(self):
        paper, created = functions.paper.create('Paper')
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        paper2 = functions.paper.get.by_term('Paper')
        self.assertIsNotNone(paper)
        self.assertEquals(paper, paper2)


    def test_paper_list(self):
        paper, created = functions.paper.create('Paper')
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        paper, created = functions.paper.create('Paper Two')
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        papers = functions.paper.list.all()
        self.assertEquals(len(papers), 2)

        papers = functions.paper.list.by_term('Two')
        self.assertEquals(len(papers), 1)


    def test_paper_acquisition(self):
        paper, created = functions.paper.create('Super Important Stuff', published_on='2016-06-01')
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        acquisition = functions.paper.acquisition.add(paper, date='2016-06-02', price=2.5)
        self.assertIsNotNone(acquisition)
        self.assertEquals(paper.acquisitions.count(), 1)

        functions.paper.acquisition.edit(paper, acquisition.id, 'price', 5.75)
        self.assertIsNotNone(acquisition.price, 5.75)


        functions.paper.acquisition.delete(paper, acquisition.id)
        self.assertEquals(paper.acquisitions.count(), 0)


    def test_paper_read(self):
        paper, created = functions.paper.create('Super Important Stuff (Second Edition)', published_on='2016-07-01')
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        read = functions.paper.read.add(paper, started='2016-07-03')
        self.assertIsNotNone(read)
        self.assertEquals(paper.reads.count(), 1)

        functions.paper.read.edit(paper, read.id, 'finished', '2016-07-15')
        self.assertIsNotNone(str(read.finished), '2016-07-15')


        functions.paper.read.delete(paper, read.id)
        self.assertEquals(paper.reads.count(), 0)
