# -*- coding: utf-8 -*-
# Copyright (C) 2017 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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
from bindings import functions


class BindingFunctionsTestCase(TestCase):
    def test_binding_create(self):
        binding, created = functions.binding.create('Taschenbuch')
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

    def test_binding_edit(self):
        binding, created = functions.binding.create('EBook')
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

        functions.binding.edit(binding, 'name', 'E-Book')
        self.assertEquals('E-Book', binding.name)

    def test_binding_get(self):
        binding, created = functions.binding.create('Gebundene Ausgabe')
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

        binding2 = functions.binding.get.by_term('Gebundene Ausgabe')
        self.assertIsNotNone(binding2)
        self.assertEquals(binding, binding2)

        binding2 = functions.binding.get.by_term(str(binding.id))
        self.assertIsNotNone(binding2)
        self.assertEquals(binding, binding2)

    def test_binding_list(self):
        binding, created = functions.binding.create('Broschiert')
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

        binding, created = functions.binding.create('Paperback')
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

        binding, created = functions.binding.create('Leather Binding')
        self.assertTrue(created)
        self.assertIsNotNone(binding.id)

        bindings = functions.binding.list.all()
        self.assertEquals(3, len(bindings))

        bindings = functions.binding.list.by_term('leather')
        self.assertEquals(1, len(bindings))
