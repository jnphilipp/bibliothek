# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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

import utils

from django.utils.translation import ugettext_lazy as _
from bindings.functions import binding as fbinding


def _binding(args):
    if args.subparser == 'add':
        binding, created = fbinding.create(args.name)
        if created:
            msg = _(f'Successfully added binding "{binding.name}" with id ' +
                    f'"{binding.id}".')
            utils.stdout.p([msg], '=')
            fbinding.stdout.info(binding)
        else:
            msg = _(f'The binding "{binding.name}" already exists with id ' +
                    f'"{binding.id}", aborting...')
            utils.stdout.p([msg], '')
    elif args.subparser == 'delete':
        binding = fbinding.get.by_term(args.binding)
        if binding:
            fbinding.delete(binding)
            msg = _(f'Successfully deleted binding with id "{binding.id}".')
            utils.stdout.p([msg], '')
        else:
            utils.stdout.p([_('No binding found.')], '')
    elif args.subparser == 'edit':
        binding = fbinding.get.by_term(args.binding)
        if binding:
            fbinding.edit(binding, args.field, args.value)
            msg = _(f'Successfully edited binding "{binding.name}" with id ' +
                    f'"{binding.id}".')
            utils.stdout.p([msg], '')
            fbinding.stdout.info(binding)
        else:
            utils.stdout.p([_('No binding found.')], '')
    elif args.subparser == 'info':
        binding = fbinding.get.by_term(args.binding)
        if binding:
            fbinding.stdout.info(binding)
        else:
            utils.stdout.p([_('No binding found.')], '')
    elif args.subparser == 'list':
        if args.search:
            bindings = fbinding.list.by_term(args.search)
        else:
            bindings = fbinding.list.all()
        fbinding.stdout.list(bindings)


def add_subparser(parser):
    binding_parser = parser.add_parser('binding', help=_('Manage bindings'))
    binding_parser.set_defaults(func=_binding)
    subparser = binding_parser.add_subparsers(dest='subparser')

    # binding add
    add_parser = subparser.add_parser('add', help=_('Add a new binding'))
    add_parser.add_argument('name', help=_('Name'))

    # binding delete
    delete_parser = subparser.add_parser('delete', help=_('Delete a binding'))
    delete_parser.add_argument('binding', help=_('Binding'))

    # binding edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a binding'))
    edit_parser.add_argument('binding', help=_('Binding'))
    edit_parser.add_argument('field', choices=['name'],
                             help=_('Which field to edit'))
    edit_parser.add_argument('value', help=_('New value for field'))

    # binding info
    info_parser = subparser.add_parser('info', help=_('Show binding info'))
    info_parser.add_argument('binding', help=_('Binding'))

    # binding list
    list_parser = subparser.add_parser('list', help=_('List bindings'))
    list_parser.add_argument('--search', help=_('Filter by name'))
