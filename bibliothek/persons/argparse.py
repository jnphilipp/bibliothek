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
from persons.functions import person as fperson


def _person(args):
    if args.subparser == 'add':
        person, created = fperson.create(args.name, args.link)
        if created:
            msg = _(f'Successfully added person "{person.name}" with id ' +
                    f'"{person.id}".')
            utils.stdout.p([msg], '=')
            fperson.stdout.info(person)
        else:
            msg = _(f'The person "{person.name}" already exists with id ' +
                    f'"{person.id}", aborting...')
            utils.stdout.p([msg], '')
    elif args.subparser == 'edit':
        person = fperson.get.by_term(args.person)
        if person:
            fperson.edit(person, args.field, args.value)
            msg = _(f'Successfully edited person "{person.name}" with id ' +
                    f'"{person.id}".')
            utils.stdout.p([msg], '')
            fperson.stdout.info(person)
        else:
            utils.stdout.p([_('No person found.')], '')
    elif args.subparser == 'info':
        person = fperson.get.by_term(args.person)
        if person:
            fperson.stdout.info(person)
        else:
            utils.stdout.p([_('No person found.')], '')
    elif args.subparser == 'list':
        if args.search:
            persons = fperson.list.by_term(args.search)
        else:
            persons = fperson.list.all()
        fperson.stdout.list(persons)


def add_subparser(parser):
    person_parser = parser.add_parser('person', help=_('Manage persons'))
    person_parser.set_defaults(func=_person)
    subparser = person_parser.add_subparsers(dest='subparser')

    # person add
    add_parser = subparser.add_parser('add', help=_('Add a person'))
    add_parser.add_argument('name', help=_('Name'))
    add_parser.add_argument('--link', nargs='*', default=[], help=_('Links'))

    # person edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a person'))
    edit_parser.add_argument('person', help=_('Person'))
    edit_parser.add_argument('field', choices=['name', 'link'],
                             help=_('Which field to edit'))
    edit_parser.add_argument('value', help=_('New value for field'))

    # person info
    info_parser = subparser.add_parser('info', help=_('Show person info'))
    info_parser.add_argument('person', help=_('Person'))

    # person list
    list_parser = subparser.add_parser('list', help=_('List persons'))
    list_parser.add_argument('--search', help=_('Filter persons by term'))
