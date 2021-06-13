# -*- coding: utf-8 -*-
# Copyright (C) 2016-2021 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
from io import StringIO
from languages.models import Language


class LanguageModelTestCase(TestCase):
    def test_from_to_dict(self):
        language, created = Language.objects.get_or_create(name="English")
        self.assertTrue(created)
        self.assertIsNotNone(language.id)
        self.assertEquals({"name": "English"}, language.to_dict())
        self.assertEquals((language, False), Language.from_dict({"name": "English"}))

    def test_edit(self):
        language, created = Language.objects.get_or_create(name="Englisch")
        self.assertTrue(created)
        self.assertIsNotNone(language.id)

        language.edit("name", "English")
        self.assertEquals("English", language.name)

    def test_delete(self):
        language, created = Language.from_dict({"name": "English"})
        self.assertTrue(created)
        self.assertIsNotNone(language.id)

        deleted = language.delete()
        self.assertIsNone(language.id)
        self.assertEquals((1, {"languages.Language": 1}), deleted)

    def test_get(self):
        language, created = Language.from_dict({"name": "English"})
        self.assertTrue(created)
        self.assertIsNotNone(language.id)

        language2 = Language.get("English")
        self.assertIsNotNone(language2)
        self.assertEquals(language, language2)

        language2 = Language.get("en")
        self.assertIsNotNone(language2)
        self.assertEquals(language, language2)

        language2 = Language.get(str(language.id))
        self.assertIsNotNone(language2)
        self.assertEquals(language, language2)

    def test_get_or_create(self):
        language, created = Language.from_dict({"name": "English"})
        self.assertTrue(created)
        self.assertIsNotNone(language.id)
        self.assertEquals(1, Language.objects.count())

        language2 = Language.get_or_create("English")
        self.assertIsNotNone(language2)
        self.assertEquals(language, language2)
        self.assertEquals(1, Language.objects.count())

        language2 = Language.get_or_create(str(language.id))
        self.assertIsNotNone(language2)
        self.assertEquals(language, language2)
        self.assertEquals(1, Language.objects.count())

        language2 = Language.get_or_create("German")
        self.assertIsNotNone(language2)
        self.assertNotEquals(language, language2)
        self.assertEquals(2, Language.objects.count())

    def test_search(self):
        language, created = Language.from_dict({"name": "English"})
        self.assertTrue(created)
        self.assertIsNotNone(language.id)

        language, created = Language.from_dict({"name": "German"})
        self.assertTrue(created)
        self.assertIsNotNone(language.id)

        language, created = Language.from_dict({"name": "Spanish"})
        self.assertTrue(created)
        self.assertIsNotNone(language.id)

        languages = Language.objects.all()
        self.assertEquals(3, len(languages))

        languages = Language.search("ish")
        self.assertEquals(2, len(languages))

        languages = Language.search("an")
        self.assertEquals(2, len(languages))

    def test_print(self):
        language, created = Language.from_dict({"name": "English"})
        self.assertTrue(created)
        self.assertIsNotNone(language.id)

        with StringIO() as cout:
            language.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Name                             English                            "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

    def test_save(self):
        language = Language(name="German")
        language.save()
        self.assertIsNotNone(language.id)
        self.assertEquals("german", language.slug)

        language = Language(name="English")
        language.save()
        self.assertIsNotNone(language.id)
        self.assertEquals("english", language.slug)
