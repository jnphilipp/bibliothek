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

from journals.functions import journal as fjournal
from django.utils.translation import ugettext_lazy as _


def _journal(args):
    if args.subparser == 'add':
        journal, created = fjournal.create(args.name)
        if created:
            msg = _(f'Successfully added journal "{journal.name}" with id ' +
                    f'"{journal.id}".')
            utils.stdout.p([msg], '=')
            fjournal.stdout.info(journal)
        else:
            msg = _(f'The journal "{journal.name}" already exists with id ' +
                    f'"{journal.id}", aborting...')
            utils.stdout.p([msg], '')
    elif args.subparser == 'delete':
        journal = fjournal.get.by_term(args.journal)
        if journal:
            fjournal.delete(journal)
            msg = _(f'Successfully deleted journal with id "{journal.id}".')
            utils.stdout.p([msg], '')
        else:
            utils.stdout.p([_('No journal found.')], '')
    elif args.subparser == 'edit':
        journal = fjournal.get.by_term(args.journal)
        if journal:
            fjournal.edit(journal, args.field, args.value)
            msg = _(f'Successfully edited journal "{journal.name}" with id ' +
                    f'"{journal.id}".')
            utils.stdout.p([msg], '')
            fjournal.stdout.info(journal)
        else:
            utils.stdout.p([_('No journal found.')], '')
    elif args.subparser == 'info':
        journal = fjournal.get.by_term(args.journal)
        if journal:
            fjournal.stdout.info(journal)
        else:
            utils.stdout.p([_('No journal found.')], '')
    elif args.subparser == 'list':
        if args.search:
            journals = fjournal.list.by_term(args.search)
        else:
            journals = fjournal.list.all()
        fjournal.stdout.list(journals)


def add_subparser(parser):
    journal_parser = parser.add_parser('journal', help=_('Manage journals'))
    journal_parser.set_defaults(func=_journal)
    subparser = journal_parser.add_subparsers(dest='subparser')

    # journal add
    add_parser = subparser.add_parser('add', help=_('Add a journal'))
    add_parser.add_argument('name', help='name')
    add_parser.add_argument('--link', nargs='*', default=[], help=_('Links'))

    # journal delete
    delete_parser = subparser.add_parser('delete', help=_('Delete a journal'))
    delete_parser.add_argument('journal', help=_('Journal'))

    # journal edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a journal'))
    edit_parser.add_argument('journal', help=_('Journal'))
    edit_parser.add_argument('field', choices=['name', 'link'],
                             help=_('Which field to edit'))
    edit_parser.add_argument('value', help=_('New value for field'))

    # journal info
    info_parser = subparser.add_parser('info', help=_('Show journal info'))
    info_parser.add_argument('journal', help=_('Journal'))

    # journal list
    list_parser = subparser.add_parser('list', help=_('List journals'))
    list_parser.add_argument('--search', help=_('Filter journals by term'))
