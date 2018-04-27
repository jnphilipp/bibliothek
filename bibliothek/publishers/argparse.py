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
from publishers.functions import publisher as fpublisher


def _publisher(args):
    if args.subparser == 'add':
        fpublisher.create(args.name, args.link)
    elif args.subparser == 'edit':
        publisher = fpublisher.get.by_term(args.publisher)
        if publisher:
            fpublisher.edit(publisher, args.field, args.value)
    elif args.subparser == 'info':
        publisher = fpublisher.get.by_term(args.publisher)
        if publisher:
            fpublisher.info(publisher)
    elif args.subparser == 'list':
        if args.search:
            fpublisher.list.by_term(args.search)
        else:
            fpublisher.list.all()


def add_subparser(parser):
    publisher_parser = parser.add_parser('publisher',
                                         help=_('Manage publishers'))
    publisher_parser.set_defaults(func=_publisher)
    subparser = publisher_parser.add_subparsers(dest='subparser')

    # publisher add
    add_parser = subparser.add_parser('add', help=_('Add a publisher'))
    add_parser.add_argument('name', help=_('Name'))
    add_parser.add_argument('--link', nargs='*', default=[], help=_('Links'))

    # publisher edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a publisher'))
    edit_parser.add_argument('publisher', help=_('Publisher'))
    edit_parser.add_argument('field', choices=['name', 'link'],
                             help=_('Which field to edit'))
    edit_parser.add_argument('value', help=_('New value for field'))

    # publisher info
    info_parser = subparser.add_parser('info', help=_('Show publisher info'))
    info_parser.add_argument('publisher', help=_('Publisher'))

    # publisher list
    list_parser = subparser.add_parser('list', help=_('List publishers'))
    list_parser.add_argument('--search', help=_('Filter publishers by term'))
