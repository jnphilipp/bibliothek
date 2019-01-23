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

from bibliothek.argparse import valid_date
from books.functions import edition as fedition
from django.utils.translation import ugettext_lazy as _
from magazines.functions import issue as fissue
from papers.functions import paper as fpaper
from shelves.functions import read as fread


def _read(args):
    if args.subparser == 'add':
        edition = fedition.get.by_term(args.obj)
        paper = fpaper.get.by_term(args.obj)
        issue = fissue.get.by_term(args.obj)

        obj = None
        if edition is None and paper is None and issue is None:
            utils.stdout.p(['Nothing found.'], '')
            return
        elif edition is not None and paper is None and issue is None:
            obj = edition
        elif edition is None and paper is not None and issue is None:
            obj = paper
        elif edition is None and paper is None and issue is not None:
            obj = issue

        if obj:
            read = fread.create(obj, args.started, args.finished)
            fread.stdout.info(read)
        else:
            utils.stdout.p(['More than one found.'], '')
    elif args.subparser == 'edit':
        read = fread.get.by_term(args.read)
        if read:
            fread.edit(read, args.field, args.value)
            utils.stdout.p([_(f'Successfully edited read "{read.id}".')], '')
        else:
            utils.stdout.p(['Nothing found.'], '')
    elif args.subparser == 'delete':
        read = fread.get.by_term(args.read)
        if read:
            fread.delete(read)
            utils.stdout.p([_(f'Successfully deleted read "{read.id}".')], '')
        else:
            utils.stdout.p(['Nothing found.'], '')
    elif args.subparser == 'info':
        read = fread.get.by_term(args.read)
        if read:
            fread.stdout.info(read)
        else:
            utils.stdout.p(['Nothing found.'], '')


def add_subparser(parser):
    read_parser = parser.add_parser('read', help=_('Manage reads'))
    read_parser.set_defaults(func=_read)
    subparser = read_parser.add_subparsers(dest='subparser')

    # read add
    add_parser = subparser.add_parser('add', help=_('Add a read'))
    add_parser.add_argument('obj', help=_('Edition, Paper or Issue'))
    add_parser.add_argument('--started', default=None, type=valid_date,
                            help=_('Date started'))
    add_parser.add_argument('--finished', default=None, type=valid_date,
                            help=_('Date finished'))

    # read delete
    delete_parser = subparser.add_parser('delete', help=_('Delete a read'))
    delete_parser.add_argument('read', help=_('Read'))

    # read edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a read'))
    edit_parser.add_argument('read', help=_('Read'))
    edit_parser.add_argument('field', choices=['started', 'finished'],
                             help=_('Which field to edit'))
    edit_parser.add_argument('value', type=valid_date,
                             help=_('New value for field'))

    # read info
    info_parser = subparser.add_parser('info', help=_('Show read info'))
    info_parser.add_argument('read', help=_('Read'))


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
