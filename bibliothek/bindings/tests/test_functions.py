# -*- coding: utf-8 -*-

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
