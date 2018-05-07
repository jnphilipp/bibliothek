#!/usr/bin/env python3
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

from bibliothek.argparse import valid_date
from django.utils.translation import ugettext_lazy as _
from persons.functions import person as fperson


def _person(args):
    if args.subparser == 'add':
        fperson.create(args.first_name, args.last_name, args.link)
    elif args.subparser == 'edit':
        person = fperson.get.by_term(args.person)
        if person:
            fperson.edit(person, args.field, args.value)
    elif args.subparser == 'info':
        person = fperson.get.by_term(args.person)
        if person:
            fperson.info(person)
    elif args.subparser == 'list':
        if args.search:
            fperson.list.by_term(args.search)
        else:
            fperson.list.all()


def add_subparser(parser):
    person_parser = parser.add_parser('person', help=_('Manage persons'))
    person_parser.set_defaults(func=_person)
    subparser = person_parser.add_subparsers(dest='subparser')

    # person add
    add_parser = subparser.add_parser('add', help=_('Add a person'))
    add_parser.add_argument('first_name', help=_('First name'))
    add_parser.add_argument('last_name', help=_('Last name'))
    add_parser.add_argument('--link', nargs='*', default=[], help=_('Links'))

    # person edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a person'))
    edit_parser.add_argument('person', help=_('Person'))
    edit_parser.add_argument('field',
                             choices=['first-name', 'last-name', 'link'],
                             help=_('Which field to edit'))
    edit_parser.add_argument('value', help=_('New value for field'))

    # person info
    info_parser = subparser.add_parser('info', help=_('Show person info'))
    info_parser.add_argument('person', help=_('Person'))

    # person list
    list_parser = subparser.add_parser('list', help=_('List persons'))
    list_parser.add_argument('--search', help=_('Filter persons by term'))
