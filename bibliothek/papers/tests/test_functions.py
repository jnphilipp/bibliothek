# -*- coding: utf-8 -*-

from django.test import TestCase
from papers import functions


class PaperFunctionsTestCase(TestCase):
    def test_paper_create(self):
        paper, created = functions.paper.create('Paper')
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        paper, created = functions.paper.create('Science Paper', ['Mark Tauser'], '2016-05-03', 'Science Journal', '20160501')
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)
        self.assertEquals(1, paper.authors.count())
        self.assertEquals('Mark', paper.authors.first().first_name)
        self.assertEquals('Tauser', paper.authors.first().last_name)
        self.assertIsNotNone(paper.journal.id)

        paper, created = functions.paper.create('AI Paper', ['Mark Tauser'], '2016-06-03', 'Science Journal', '20160603', languages=['English'])
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)
        self.assertEquals(1, paper.authors.count())
        self.assertEquals('Mark', paper.authors.first().first_name)
        self.assertEquals('Tauser', paper.authors.first().last_name)
        self.assertIsNotNone(paper.journal.id)
        self.assertEquals('Science Journal', paper.journal.name)
        self.assertEquals(1, paper.languages.count())
        self.assertEquals('English', paper.languages.first().name)


    def test_paper_parse(self):
        paper, created, acquisition = functions.paper.parse.from_dict({'title':'Parsed Paper'})
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)
        self.assertIsNotNone(acquisition.id)

        paper, created, acquisition = functions.paper.parse.from_dict({'title':'Parsed Paper Next Gen', 'authors':[{'first_name':'Jen', 'last_name':'Yen'}], 'journal':'Science Journal', 'volume':'20160603', 'published_on':'2016-06-03', 'url':'https://papers.com/paper20160603'})
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)
        self.assertIsNotNone(acquisition.id)
        self.assertEquals(1, paper.authors.count())
        self.assertEquals('Jen', paper.authors.first().first_name)
        self.assertEquals('Yen', paper.authors.first().last_name)
        self.assertIsNotNone(paper.journal.id)
        self.assertEquals(1, paper.links.count())
        self.assertIsNotNone(paper.links.first().id)


    def test_paper_edit(self):
        paper, created = functions.paper.create('Paper 2')
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        functions.paper.edit(paper, 'title', 'Paper Two')
        self.assertEquals('Paper Two', paper.title)

        functions.paper.edit(paper, 'journal', 'Science Journal')
        self.assertIsNotNone(paper.journal.id)
        self.assertEquals('Science Journal', paper.journal.name)

        functions.paper.edit(paper, '+language', 'Deutsch')
        self.assertEquals(1, paper.languages.count())
        self.assertEquals('Deutsch', paper.languages.first().name)

        functions.paper.edit(paper, '+language', 'English')
        self.assertEquals(2, paper.languages.count())
        self.assertEquals('English', paper.languages.last().name)

        functions.paper.edit(paper, '-language', 'Deutsch')
        self.assertEquals(1, paper.languages.count())
        self.assertEquals('English', paper.languages.first().name)


    def test_paper_get(self):
        paper, created = functions.paper.create('Paper')
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        paper2 = functions.paper.get.by_term('Paper')
        self.assertIsNotNone(paper)
        self.assertEquals(paper, paper2)

        paper2 = functions.paper.get.by_term(str(paper.id))
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
        self.assertEquals(2, len(papers))

        papers = functions.paper.list.by_term('Two')
        self.assertEquals(1, len(papers))


    def test_paper_acquisition(self):
        paper, created = functions.paper.create('Super Important Stuff', published_on='2016-06-01')
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        acquisition = functions.paper.acquisition.add(paper, date='2016-06-02', price=2.5)
        self.assertIsNotNone(acquisition)
        self.assertEquals(1, paper.acquisitions.count())

        functions.paper.acquisition.edit(paper, acquisition.id, 'price', 5.75)
        self.assertIsNotNone(5.75, acquisition.price)


        functions.paper.acquisition.delete(paper, acquisition.id)
        self.assertEquals(0, paper.acquisitions.count())


    def test_paper_read(self):
        paper, created = functions.paper.create('Super Important Stuff (Second Edition)', published_on='2016-07-01')
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        read = functions.paper.read.add(paper, started='2016-07-03')
        self.assertIsNotNone(read)
        self.assertEquals(1, paper.reads.count())

        functions.paper.read.edit(paper, read.id, 'finished', '2016-07-15')
        self.assertIsNotNone('2016-07-15', str(read.finished))

        functions.paper.read.delete(paper, read.id)
        self.assertEquals(0, paper.reads.count())
