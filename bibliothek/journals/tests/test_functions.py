# -*- coding: utf-8 -*-

from django.test import TestCase
from journals import functions


class JournalFunctionsTestCase(TestCase):
    def test_journal_create(self):
        journal, created = functions.journal.create('Test Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal, created = functions.journal.create('Scince Journal', ['https://sj.com'])
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)


    def test_journal_edit(self):
        journal, created = functions.journal.create('Test2 Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        functions.journal.edit(journal, 'name', 'IEEE Journal')
        self.assertEquals('IEEE Journal', journal.name)


    def test_journal_get(self):
        journal, created = functions.journal.create('Space Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal2 = functions.journal.get.by_term('Space Journal')
        self.assertIsNotNone(journal2)
        self.assertEquals(journal, journal2)

        journal2 = functions.journal.get.by_term(str(journal.id))
        self.assertIsNotNone(journal2)
        self.assertEquals(journal, journal2)


    def test_journal_list(self):
        journal, created = functions.journal.create('Medicine Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal, created = functions.journal.create('Math Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal, created = functions.journal.create('All new stuff about Math')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journals = functions.journal.list.all()
        self.assertEquals(3, len(journals))

        journals = functions.journal.list.by_term('Journal')
        self.assertEquals(2, len(journals))
