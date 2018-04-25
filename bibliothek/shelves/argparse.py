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


def acquisition_subparser(parser, arg_name, help_txt):
    acquisition_parser = parser.add_parser('acquisition',
                                           help=_('Manage acquisition'))
    acquisition_parser.add_argument(arg_name, help=help_txt)
    subparser = acquisition_parser.add_subparsers(dest='acquisition_subparser')

    add_parser = subparser.add_parser('add', help=_('Add an acquisition'))
    add_parser.add_argument('--date', default=None, type=valid_date,
                            help=_('Date'))
    add_parser.add_argument('--price', default=0, type=float, help=_('Price'))

    delete_parser = subparser.add_parser('delete',
                                         help=_('Delete an acquisition'))
    delete_parser.add_argument('acquisition',  type=int, help=_('Acquisition'))

    edit_parser = subparser.add_parser('edit', help=_('Edit an acquisition'))
    edit_parser.add_argument('acquisition', type=int, help=_('Acquisition'))

    edit_subparser = edit_parser.add_subparsers(dest='edit_subparser',
                                                help=_('Which field to edit'))
    edit_date_parser = edit_subparser.add_parser('date')
    edit_date_parser.add_argument('value', type=valid_date,
                                  help=_('New value for field'))

    edit_price_parser = edit_subparser.add_parser('price')
    edit_price_parser.add_argument('value', type=float,
                                   help=_('New value for field'))


def read_subparser(parser, arg_name, help_txt):
    read_parser = parser.add_parser('read', help=_('Manage read'))
    read_parser.add_argument(arg_name, help=help_txt)
    subparser = read_parser.add_subparsers(dest='read_subparser')

    add_parser = subparser.add_parser('add', help=_('Add a read'))
    add_parser.add_argument('--started', default=None, type=valid_date,
                            help=_('Date started'))
    add_parser.add_argument('--finished', default=None, type=valid_date,
                            help=_('Date finished'))

    delete_parser = subparser.add_parser('delete', help=_('Delete a read'))
    delete_parser.add_argument('read', type=int, help=_('Read'))

    edit_parser = subparser.add_parser('edit', help=_('Edit a read'))
    edit_parser.add_argument('read', type=int, help=_('Read'))
    edit_parser.add_argument('field', choices=['started', 'finished'],
                             help=_('Which field to edit'))
    edit_parser.add_argument('value', type=valid_date,
                             help=_('New value for field'))
