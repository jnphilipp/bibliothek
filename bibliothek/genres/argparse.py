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

from genres.functions import genre as fgenre
from django.utils.translation import ugettext_lazy as _


def _genre(args):
    if args.subparser == 'add':
        fgenre.create(args.name)
    elif args.subparser == 'edit':
        genre = fgenre.get.by_term(args.genre)
        if genre:
            fgenre.edit(genre, args.field, args.value)
    elif args.subparser == 'info':
        genre = fgenre.get.by_term(args.genre)
        if genre:
            fgenre.info(genre)
    elif args.subparser == 'list':
        if args.search:
            fgenre.list.by_term(args.search)
        else:
            fgenre.list.all()


def add_subparser(parser):
    genre_parser = parser.add_parser('genre', help=_('Manage genres'))
    genre_parser.set_defaults(func=_genre)
    subparser = genre_parser.add_subparsers(dest='subparser')

    # genre add
    add_parser = subparser.add_parser('add', help=_('Add a genre'))
    add_parser.add_argument('name', help=_('Name'))

    # genre edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a genre'))
    edit_parser.add_argument('genre', help=_('Genre'))
    edit_parser.add_argument('field', choices=['name'],
                             help=_('Which field to edit'))
    edit_parser.add_argument('value', help=_('New value for field'))

    # genre info
    info_parser = subparser.add_parser('info', help=_('Show genre info'))
    info_parser.add_argument('genre', help=_('Genre'))

    # genre list
    list_parser = subparser.add_parser('list', help=_('List genres'))
    list_parser.add_argument('--search', help=_('Filter genres by term'))
