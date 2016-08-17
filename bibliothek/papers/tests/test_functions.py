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
