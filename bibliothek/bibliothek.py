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
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliothek.settings')

import django
django.setup()

from argparse import ArgumentParser, RawTextHelpFormatter
from bibliothek import settings
from datetime import datetime
from django.db.models import Q
from utils import lookahead, stdout


def init():
    if not os.path.exists(settings.APP_DATA_DIR):
        os.makedirs(settings.APP_DATA_DIR)
        from django.core.management import execute_from_command_line
        execute_from_command_line(['', 'migrate'])


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError('Not a valid date: "{0}".'.format(s))


def _paper(args):
    import papers.functions
    if args.paper_subparsers == 'acquisition':
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
        parser_paper.print_help()


if __name__ == "__main__":
    init()


    parser = ArgumentParser(prog=settings.APP_NAME, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version=settings.APP_VERSION)
    subparsers = parser.add_subparsers(dest='subparser')


    # create the parser for the "paper" subcommand
    parser_paper = subparsers.add_parser('paper', help='subcommand for papers')
    parser_paper.set_defaults(func=_paper)
    paper_subparsers = parser_paper.add_subparsers(dest='paper_subparsers')

    paper_acquisition_parser = paper_subparsers.add_parser('acquisition', help='manage acquisition of papers')
    paper_acquisition_parser.add_argument('action', choices=['add', 'delete'], help='action to perform')
    paper_acquisition_parser.add_argument('paper', nargs='?', help='which paper')

    paper_edit_parser = paper_subparsers.add_parser('edit', help='edit paper')
    paper_edit_parser.add_argument('paper', help='which paper to edit')
    paper_edit_parser.add_argument('field', choices=['title', 'published_on', 'volume'], help='which field to edit')
    paper_edit_parser.add_argument('value', help='new value for the field')

    paper_list_parser = paper_subparsers.add_parser('list', help='list papers')
    paper_list_parser.add_argument('shelf', choices=['read', 'unread'], nargs='?', help='filter on shelves')

    paper_info_parser = paper_subparsers.add_parser('info', help='show information of a paper')
    paper_info_parser.add_argument('paper', nargs='?', help='which paper to show')

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

    args = parser.parse_args()
    if args.subparser:
        args.func(args)
    else:
        parser.print_usage()
