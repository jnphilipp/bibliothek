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
from journals.functions import journal as fjournal


class JournalFunctionsTestCase(TestCase):
    def test_journal_create(self):
        journal, created = fjournal.create('Test Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal, created = fjournal.create('Scince Journal',
                                           ['https://sj.com'])
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

    def test_journal_edit(self):
        journal, created = fjournal.create('Test2 Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        fjournal.edit(journal, 'name', 'IEEE Journal')
        self.assertEquals('IEEE Journal', journal.name)

        fjournal.edit(journal, 'link', 'https://test.com')
        self.assertEquals(1, journal.links.count())
        self.assertEquals('https://test.com', journal.links.first().link)

        fjournal.edit(journal, 'link', 'https://example.com')
        self.assertEquals(2, journal.links.count())
        self.assertEquals('https://example.com', journal.links.first().link)

        fjournal.edit(journal, 'link', 'https://test.com')
        self.assertEquals(1, journal.links.count())
        self.assertEquals('https://example.com', journal.links.first().link)

    def test_journal_get(self):
        journal, created = fjournal.create('Space Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal2 = fjournal.get.by_term('Space Journal')
        self.assertIsNotNone(journal2)
        self.assertEquals(journal, journal2)

        journal2 = fjournal.get.by_term(str(journal.id))
        self.assertIsNotNone(journal2)
        self.assertEquals(journal, journal2)

    def test_journal_list(self):
        journal, created = fjournal.create('Medicine Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal, created = fjournal.create('Math Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal, created = fjournal.create('All new stuff about Math')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journals = fjournal.list.all()
        self.assertEquals(3, len(journals))

        journals = fjournal.list.by_term('Journal')
        self.assertEquals(2, len(journals))
