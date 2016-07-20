#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""bibliothek
Copyright (C) 2016 jnphilipp <me@jnphilipp.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliothek.settings')

import django
django.setup()

from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from bibliothek import settings
from datetime import datetime
from utils import lookahead, stdout


def init():
    from django.core.management import execute_from_command_line
    if settings.DEBUG:
        execute_from_command_line(['', 'migrate'])
    else:
        if not os.path.exists(settings.APP_DATA_DIR):
            os.makedirs(settings.APP_DATA_DIR)
            execute_from_command_line(['', 'migrate'])


def valid_date(s):
    try:
        if s.lower() in ['', 'n', 'none', 'null']:
            return None
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise ArgumentTypeError('Not a valid date: "{0}".'.format(s))


def _journal(args):
    import journals.functions
    if args.journal_subparsers == 'list':
        if args.shelf:
            journals.functions.journal.list.by_shelf(args.shelf)
        elif args.search:
            journals.functions.journal.list.by_search(args.search)
    else:
        journal_parser.print_help()


def _paper(args):
    import papers.functions
    if args.paper_subparsers == 'acquisition':
        if args.paper_acquisition_subparsers == 'add':
            paper = papers.functions.paper.get.by_term(args.paper)
            if paper:
                papers.functions.paper.acquisition.add(paper, args.started, args.finished)
        elif args.paper_acquisition_subparsers == 'delete':
            paper = papers.functions.paper.get.by_term(args.paper)
            if paper:
                papers.functions.paper.acquisition.delete(paper, args.id)
        elif args.paper_acquisition_subparsers == 'edit':
            print(args)
            paper = papers.functions.paper.get.by_term(args.paper)
            if paper:
                papers.functions.paper.acquisition.edit(paper, args.id, args.paper_acquisition_edit_subparsers, args.value)
    elif args.paper_subparsers == 'edit':
        paper = papers.functions.paper.get.by_term(args.paper)
        if paper:
            papers.functions.paper.edit.cmd(args.paper)
    elif args.paper_subparsers == 'list':
        papers.functions.paper.list.by_shelf(args.shelf)
    elif args.paper_subparsers == 'info':
        paper = papers.functions.paper.get.by_term(args.paper)
        if paper:
            papers.functions.paper.info.show(paper)
    elif args.paper_subparsers == 'open':
        paper = papers.functions.paper.get.by_term(args.paper)
        if paper:
            file = paper.files.get(pk=args.id)
            path = os.path.join(settings.MEDIA_ROOT, file.file.path)
            if sys.platform == 'linux':
                os.system('xdg-open "%s"' % path)
            else:
                os.system('open "%s"' % path)
    elif args.paper_subparsers == 'parse':
        papers.functions.paper.create.from_bibtex(args.bibtex, args.file)
    elif args.paper_subparsers == 'read':
        if args.paper_read_subparsers == 'add':
            paper = papers.functions.paper.get.by_term(args.paper)
            if paper:
                papers.functions.paper.read.add(paper, args.started, args.finished)
        elif args.paper_read_subparsers == 'delete':
            paper = papers.functions.paper.get.by_term(args.paper)
            if paper:
                papers.functions.paper.read.delete(paper, args.id)
        elif args.paper_read_subparsers == 'edit':
            paper = papers.functions.paper.get.by_term(args.paper)
            if paper:
                papers.functions.paper.read.edit(paper, args.id, args.field, args.value)
    else:
        paper_parser.print_help()


def _runserver(args):
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    init()


    parser = ArgumentParser(prog=settings.APP_NAME, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version=settings.APP_VERSION)
    subparsers = parser.add_subparsers(dest='subparser')


    # create the parser for the "journal" subcommand
    journal_parser = subparsers.add_parser('journal', help='subcommand for journals')
    journal_parser.set_defaults(func=_journal)
    journal_subparsers = journal_parser.add_subparsers(dest='journal_subparsers')

    # journal list
    journal_list_parser = journal_subparsers.add_parser('list', help='list journals')
    journal_list_parser.add_argument('-shelf', choices=['read', 'unread'], help='filter on shelves')
    journal_list_parser.add_argument('-s', '--search', help='filter on shelves')


    # create the parser for the "paper" subcommand
    paper_parser = subparsers.add_parser('paper', help='subcommand for papers')
    paper_parser.set_defaults(func=_paper)
    paper_subparsers = paper_parser.add_subparsers(dest='paper_subparsers')

    # paper acquisitions
    paper_acquisition_parser = paper_subparsers.add_parser('acquisition', help='manage acquisition of papers')
    paper_acquisition_subparser = paper_acquisition_parser.add_subparsers(dest='paper_acquisition_subparsers')

    paper_acquisition_add_parser = paper_acquisition_subparser.add_parser('add', help='manage addition of acquisitions')
    paper_acquisition_add_parser.add_argument('paper', help='which paper to edit')
    paper_acquisition_add_parser.add_argument('-date', default=None, type=valid_date, help='date')
    paper_acquisition_add_parser.add_argument('-price', default=None, type=float, help='price')

    paper_acquisition_edit_parser = paper_acquisition_subparser.add_parser('edit', help='manage edition of acquisitions')
    paper_acquisition_edit_parser.add_argument('paper', help='which paper to edit')
    paper_acquisition_edit_parser.add_argument('id', type=int, help='which acquisition to edit')

    paper_acquisition_edit_subparser = paper_acquisition_edit_parser.add_subparsers(dest='paper_acquisition_edit_subparsers', help='which field to edit')
    paper_acquisition_edit_date_parser = paper_acquisition_edit_subparser.add_parser('date')
    paper_acquisition_edit_date_parser.add_argument('value', type=valid_date, help='new value for field')

    paper_acquisition_edit_date_parser = paper_acquisition_edit_subparser.add_parser('price')
    paper_acquisition_edit_date_parser.add_argument('value', type=float, help='new value for field')

    paper_acquisition_delete_parser = paper_acquisition_subparser.add_parser('delete', help='manage deletion of acquisitions')
    paper_acquisition_delete_parser.add_argument('paper', help='which paper to edit')
    paper_acquisition_delete_parser.add_argument('id', type=int, help='which acquisition to delete')

    # paper edit
    paper_edit_parser = paper_subparsers.add_parser('edit', help='edit paper')
    paper_edit_parser.add_argument('paper', help='which paper to edit')
    paper_edit_parser.add_argument('field', choices=['title', 'published_on', 'volume'], help='which field to edit')
    paper_edit_parser.add_argument('value', help='new value for the field')

    # paper list
    paper_list_parser = paper_subparsers.add_parser('list', help='list papers')
    paper_list_parser.add_argument('shelf', choices=['read', 'unread'], nargs='?', help='filter on shelves')

    # paper info
    paper_info_parser = paper_subparsers.add_parser('info', help='show information of a paper')
    paper_info_parser.add_argument('paper', nargs='?', help='which paper to show')

    # paper open
    paper_open_parser = paper_subparsers.add_parser('open', help='open a file of a paper')
    paper_open_parser.add_argument('paper', nargs='?', help='which paper to show')
    paper_open_parser.add_argument('id', type=int, help='which file to open')

    # paper parse
    paper_parse_parser = paper_subparsers.add_parser('parse', help='parse bibtex and add papers')
    paper_parse_parser.add_argument('bibtex', help='bibtex file')
    paper_parse_parser.add_argument('-f', '--file', nargs='*', default=[], help='files to add')

    # paper reads
    paper_read_parser = paper_subparsers.add_parser('read', help='manage read of papers')
    paper_read_subparser = paper_read_parser.add_subparsers(dest='paper_read_subparsers')

    paper_read_add_parser = paper_read_subparser.add_parser('add', help='manage addition of reads')
    paper_read_add_parser.add_argument('paper', help='which paper to edit')
    paper_read_add_parser.add_argument('-started', default=None, type=valid_date, help='date started')
    paper_read_add_parser.add_argument('-finished', default=None, type=valid_date, help='date finished')

    paper_read_edit_parser = paper_read_subparser.add_parser('edit', help='manage edition of reads')
    paper_read_edit_parser.add_argument('paper', help='which paper to edit')
    paper_read_edit_parser.add_argument('id', type=int, help='which read to edit')
    paper_read_edit_parser.add_argument('field', choices=['started', 'finished'], help='which field to edit')
    paper_read_edit_parser.add_argument('value', type=valid_date, help='new value for field')

    paper_read_delete_parser = paper_read_subparser.add_parser('delete', help='manage deletion of reads')
    paper_read_delete_parser.add_argument('paper', help='which paper to edit')
    paper_read_delete_parser.add_argument('id', type=int, help='which read to delete')


    # create the parser for the "runserver" subcommand
    runserver_parser = subparsers.add_parser('runserver', help='subcommand for local http server')
    runserver_parser.set_defaults(func=_runserver)

    args = parser.parse_args()
    if args.subparser:
        args.func(args)
    else:
        parser.print_usage()
