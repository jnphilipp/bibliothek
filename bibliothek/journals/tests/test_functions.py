# -*- coding: utf-8 -*-

from django.test import TestCase
from journals import functions


class JournalFunctionsTestCase(TestCase):
    def test_journal_create(self):
        journal, created = functions.journal.create('Test Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)


    def test_journal_edit(self):
        journal, created = functions.journal.create('Test2 Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        functions.journal.edit(journal, 'name', 'IEEE Test Journal')
        self.assertEquals(journal.name, 'IEEE Test Journal')


    def test_journal_get(self):
        journal, created = functions.journal.create('Test Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal2 = functions.journal.get.by_term('Test Journal')
        self.assertIsNotNone(journal)
        self.assertEquals(journal, journal2)


    def test_journal_list(self):
        journal, created = functions.journal.create('Test Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal, created = functions.journal.create('Test2 Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journals = functions.journal.list.all()
        self.assertEquals(len(journals), 2)
