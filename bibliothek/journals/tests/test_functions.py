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
from journals import functions


class JournalFunctionsTestCase(TestCase):
    def test_journal_create(self):
        journal, created = functions.journal.create('Test Journal')
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        journal, created = functions.journal.create('Scince Journal',
                                                    ['https://sj.com'])
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
