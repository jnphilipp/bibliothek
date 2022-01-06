# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
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

from bindings.models import Binding
from django.test import TestCase
from io import StringIO


class BindingModelTestCase(TestCase):
    def test_from_to_dict(self):
        binding, created = Binding.objects.get_or_create(name="Taschenbuch")
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)
        self.assertEquals({"name": "Taschenbuch"}, binding.to_dict())
        self.assertEquals((binding, False), Binding.from_dict({"name": "Taschenbuch"}))

    def test_edit(self):
        binding, created = Binding.objects.get_or_create(name="EBook")
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

        binding.edit("name", "E-Book")
        self.assertEquals("E-Book", binding.name)

    def test_delete(self):
        binding, created = Binding.from_dict({"name": "Taschenbuch"})
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

        deleted = binding.delete()
        self.assertIsNone(binding.id)
        self.assertEquals((1, {"bindings.Binding": 1}), deleted)

    def test_get(self):
        binding, created = Binding.from_dict({"name": "Gebundene Ausgabe"})
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

        binding2 = Binding.get("Gebundene Ausgabe")
        self.assertIsNotNone(binding2)
        self.assertEquals(binding, binding2)

        binding2 = Binding.get(str(binding.id))
        self.assertIsNotNone(binding2)
        self.assertEquals(binding, binding2)

    def test_search(self):
        binding, created = Binding.from_dict({"name": "Broschiert"})
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

        binding, created = Binding.from_dict({"name": "Paperback"})
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

        binding, created = Binding.from_dict({"name": "Leather Binding"})
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

        bindings = Binding.objects.all()
        self.assertEquals(3, len(bindings))

        bindings = Binding.search("leather")
        self.assertEquals(1, len(bindings))

        bindings = Binding.search("er")
        self.assertEquals(3, len(bindings))

    def test_print(self):
        binding, created = Binding.from_dict({"name": "Leather Binding"})
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

        with StringIO() as cout:
            binding.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Name                             Leather Binding                    "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

    def test_save(self):
        binding = Binding(name="E-Book")
        binding.save()
        self.assertIsNotNone(binding.id)
        self.assertEquals("e-book", binding.slug)

        binding = Binding(name="Taschenbuch")
        binding.save()
        self.assertIsNotNone(binding.id)
        self.assertEquals("taschenbuch", binding.slug)
