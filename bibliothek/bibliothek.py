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

def init():
    if not os.path.exists(settings.APP_DATA_DIR):
        os.makedirs(settings.APP_DATA_DIR)
        from django.core.management import execute_from_command_line
        execute_from_command_line(['', 'migrate'])

def _paper(args):
    import papers.functions
    if args.paper_subparsers == 'parse':
        papers.functions.paper.from_bibtex(args.bibtex, args.file)
    if args.paper_subparsers == 'list':
        from papers.models import Paper
        print('=' * 100)
        for paper in Paper.objects.all():
            print(paper.title)
            print('_' * 100)
        print('=' * 100)
    else:
        parser_paper.print_help()


if __name__ == "__main__":
    init()
    print(settings.MEDIA_ROOT)


    parser = ArgumentParser(prog=settings.APP_NAME, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version=settings.APP_VERSION)
    subparsers = parser.add_subparsers(dest='subparser')


    # create the parser for the "paper" subcommand
    parser_paper = subparsers.add_parser('paper', help='subcommand for papers')
    paper_subparsers = parser_paper.add_subparsers(dest='paper_subparsers')

    parser_paper_parse = paper_subparsers.add_parser('parse', help='parse bibtex and add papers')
    parser_paper_parse.add_argument('bibtex', help='bibtex file')
    parser_paper_parse.add_argument('-f', '--file', nargs='*', default=[], help='files to add')

    parser_paper_list = paper_subparsers.add_parser('list', help='list papers')

    parser_paper.set_defaults(func=_paper)

    args = parser.parse_args()
    if args.subparser:
        args.func(args)
    else:
        parser.print_usage()
