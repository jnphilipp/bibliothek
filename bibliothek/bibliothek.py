#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C)
#     2016-2020 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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

import json
import os
import sys
import time
import threading
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliothek.settings')

import django
django.setup()

import bibliothek.argparse
import bindings.argparse
import books.argparse
import genres.argparse
import journals.argparse
import magazines.argparse
import papers.argparse
import persons.argparse
import publishers.argparse
import series.argparse
import shelves.argparse

from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from datetime import date, datetime
from django.utils.translation import ugettext_lazy as _

from bibliothek import (__app_name__, __author__, __email__, __github__,
                        __version__, settings)
from utils import lookahead, stdout


def init():
    from django.core.management import execute_from_command_line
    # if settings.DEBUG:
    #     execute_from_command_line(['', 'migrate'])
    # else:
    if not os.path.exists(settings.APP_DATA_DIR):
        from django.core.management import execute_from_command_line
        os.makedirs(settings.APP_DATA_DIR)
        execute_from_command_line(['', 'migrate'])


def _runserver(args):
    from django.core.management import execute_from_command_line
    runserver_args = ['', 'runserver', args.addrport]
    if args.ipv6:
        runserver_args += ['-6']
    execute_from_command_line(runserver_args)


def _import(args):
    import bindings.functions.binding as fbinding
    import books.functions.book as fbook
    import books.functions.edition as fedition
    import genres.functions as genres_functions
    import persons.functions.person as fperson
    import publishers.functions.publisher as fpublisher
    import series.functions.series as fseries
    with open(args.path, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())

    if 'books' in data:
        for b in data['books']:
            authors = []
            for a in b['authors']:
                if 'first_name' in a:
                    name = f'{a["first_name"]} {a["last_name"]}'.strip()
                else:
                    name = a['name']
                person, c = fperson.create(name, a['links'])
                authors.append(str(person.id))

            genres = []
            for g in b['genres']:
                genre, c = genres_functions.genre.create(g['name'])
                genres.append(str(genre.id))

            series, c = fseries.create(b['series']['name'],
                                       b['series']['links'])
            book, c = fbook.create(b['title'], authors, str(series.id),
                                   b['volume'], genres, b['links'])

            for e in b['editions']:
                binding, c = fbinding.create(e['binding']['name'])
                publisher, c = fpublisher.create(e['publisher']['name'],
                                                 e['publisher']['links'])
                edition, c = fedition.create(book, e['isbn'],
                                             e['publishing_date'], e['cover'],
                                             str(binding.id),
                                             str(publisher.id), e['languages'],
                                             e['files'])

                for a in e['acquisitions']:
                    if not edition.acquisitions.filter(date=a['date']). \
                            filter(price=a['price']).exists() and \
                            (a['date'] or a['price']):
                        acquisition = fedition.acquisition.add(edition,
                                                               a['date'],
                                                               a['price'])

                for r in e['reads']:
                    if not edition.reads.filter(started=r['started']). \
                            filter(finished=r['finished']).exists() and \
                            (r['started'] or r['finished']):
                        read = fedition.read.add(edition, r['started'],
                                                 r['finished'])


def _reading_list(args):
    from books.models import Edition
    from magazines.models import Issue
    from papers.models import Paper
    from shelves.models import Acquisition

    reading_list = set()
    for acquisition in Acquisition.objects.all():
        if acquisition.content_object.reads.count() == 0:
            reading_list.add((acquisition.content_object, acquisition.date))
    reading_list = sorted(reading_list,
                          key=lambda x: x[1] if x[1] else date.min)
    if args.limit:
        reading_list = reading_list[:args.limit]

    positions = [.1, 0.15, .85, 1.]
    stdout.p([_('Type'), _('Id'), _('Title'), _('Acquisition')],
             positions=positions, after='=')
    for item, has_next in lookahead(reading_list):
        stype = ''
        if isinstance(item[0], Paper):
            stype = 'Paper'
        elif isinstance(item[0], Edition):
            stype = 'Book'
        elif isinstance(item[0], Issue):
            stype = 'Issue'
        stdout.p([stype, item[0].id, str(item[0]), item[1] if item[1] else ''],
                 positions=positions, after='_' if has_next else '=')


def _statistics(args):
    positions = [.50, .66, .82, 1.]

    from books.models import Book, Edition
    from magazines.models import Magazine, Issue
    from papers.models import Paper

    stdout.p([_('Type'), _('Count'), _('Read'),
              _('Read %(year)d' % {'year': datetime.now().year})], after='=',
             positions=positions)
    stdout.p([
        _('Books'),
        Book.objects.count(),
        Book.objects.filter(editions__reads__isnull=False).count(),
        Book.objects.filter(
            editions__reads__finished__year=datetime.now().year
        ).count()
    ], positions=positions)
    stdout.p([
        _('Editions'),
        Edition.objects.count(),
        Edition.objects.filter(reads__isnull=False).count(),
        Edition.objects.filter(
            reads__finished__year=datetime.now().year
        ).count()
    ], positions=positions)
    stdout.p([_('Magazines'), Magazine.objects.count(), 0, 0],
             positions=positions)
    stdout.p([_('Issues'), Issue.objects.count(), 0, 0],
             positions=positions)
    stdout.p([
        _('Papers'),
        Paper.objects.count(),
        Paper.objects.filter(reads__isnull=False).count(),
        Paper.objects.filter(reads__finished__year=datetime.now().year).count()
    ], positions=positions)


if __name__ == '__main__':
    init()

    parser = ArgumentParser(prog=__app_name__,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('-V', '--version', action='version',
                        version=_('%%(prog)s v%(version)s\nLizenz GPLv3+: ' +
                                  'GNU GPL Version 3 or later ' +
                                  '<https://gnu.org/licenses/gpl.html>.\n' +
                                  'Report bugs to %(github)s/issues.\n\n' +
                                  'Written by %(author)s <%(email)s>') % {
                            'version': __version__, 'github': __github__,
                            'author': __author__, 'email': __email__},)

    subparser = parser.add_subparsers(dest='subparser', metavar='COMMAND')

    # create the parser for the "info" subcommand
    bibliothek.argparse.add_subparser(subparser)

    # create the parser for the "binding" subcommand
    bindings.argparse.add_subparser(subparser)

    # create the parser for the "book" subcommand
    books.argparse.add_subparser(subparser)

    # create the parser for the "genre" subcommand
    genres.argparse.add_subparser(subparser)

    # create the parser for the "journal" subcommand
    journals.argparse.add_subparser(subparser)

    # create the parser for the "magazine" subcommand
    magazines.argparse.add_subparser(subparser)

    # create the parser for the "paper" subcommand
    papers.argparse.add_subparser(subparser)

    # create the parser for the "person" subcommand
    persons.argparse.add_subparser(subparser)

    # create the parser for the "publisher" subcommand
    publishers.argparse.add_subparser(subparser)

    # create the parser for the "series" subcommand
    series.argparse.add_subparser(subparser)

    # create the parser for the "read" subcommand
    shelves.argparse.add_subparser(subparser)

    # create the parser for the "runserver" subcommand
    runserver_parser = subparser.add_parser('runserver',
                                            help=_('Start local http server'))
    runserver_parser.set_defaults(func=_runserver)
    runserver_parser.add_argument('addrport', nargs='?',
                                  default='127.0.0.1:8000',
                                  help=_('Optional port number, or ' +
                                         'ipaddr:port'))
    runserver_parser.add_argument('-6', '--ipv6', action='store_true',
                                  help=_('Tells Django to use an IPv6 ' +
                                         'address.'))
    runserver_parser.add_argument('-b', '--background', action='store_true',
                                  help=_('Runs the Django server in the ' +
                                         'background.'))

    # create the parser for the "import" subcommand
    import_parser = subparser.add_parser('import',
                                         help=_('Import data from JSON'))
    import_parser.set_defaults(func=_import)
    import_parser.add_argument('path', help=_('JSON file'))

    # create the parser for the "reading-list" subcommand
    reading_list_parser = subparser.add_parser('reading-list',
                                               help=_('Show reading-list'))
    reading_list_parser.set_defaults(func=_reading_list)
    reading_list_parser.add_argument('--limit', type=int,
                                     help=_('Limit list to n entries'))

    # create the parser for the "statistics" subcommand
    statistics_parser = subparser.add_parser('statistics',
                                             help=_('Show statistics'))
    statistics_parser.set_defaults(func=_statistics)

    args = parser.parse_args()
    if args.subparser:
        args.func(args)
    else:
        parser.print_usage()
