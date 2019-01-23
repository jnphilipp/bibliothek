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

from bibliothek.argparse import valid_date
from django.utils.translation import ugettext_lazy as _
from series.functions import series as fseries


def _series(args):
    if args.subparser == 'add':
        fseries.create(args.name, args.link)
    elif args.subparser == 'edit':
        series_obj = fseries.get.by_term(args.series)
        if series_obj:
            fseries.edit(series_obj, args.field, args.value)
    elif args.subparser == 'info':
        series_obj = fseries.get.by_term(args.series)
        if series_obj:
            fseries.info(series_obj)
    elif args.subparser == 'list':
        if args.search:
            fseries.list.by_term(args.search)
        else:
            fseries.list.all()


def add_subparser(parser):
    series_parser = parser.add_parser('series', help=_('Manage series'))
    series_parser.set_defaults(func=_series)
    subparser = series_parser.add_subparsers(dest='subparser')

    # series add
    add_parser = subparser.add_parser('add', help=_('Add a new series'))
    add_parser.add_argument('name', help=_('Name'))
    add_parser.add_argument('--link', nargs='*', default=[], help=_('Links'))

    # series edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a series'))
    edit_parser.add_argument('series', help=_('Series'))
    edit_parser.add_argument('field', choices=['name', 'link'],
                             help=_('Which field to edit'))
    edit_parser.add_argument('value', help=_('New value for field'))

    # series info
    info_parser = subparser.add_parser('info', help=_('Show series info'))
    info_parser.add_argument('series', help=_('Series'))

    # series list
    list_parser = subparser.add_parser('list', help=_('List series'))
    list_parser.add_argument('--search', help=_('Filter series by term'))
