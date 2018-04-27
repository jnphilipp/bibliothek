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

import json
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliothek.settings')

import django
django.setup()

import bindings.argparse
import books.argparse
import genres.argparse
import journals.argparse
import magazines.argparse
import papers.argparse
import persons.argparse
import publishers.argparse

from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from datetime import date, datetime
from django.utils.translation import ugettext_lazy as _

from bibliothek import (__app_name__, __description__, __version__,
                        __license__, __author__, __email__, settings)
from utils import app_version, lookahead, stdout


def init():
    from django.core.management import execute_from_command_line
    # if settings.DEBUG:
    #     execute_from_command_line(['', 'migrate'])
    # else:
    if not os.path.exists(settings.APP_DATA_DIR):
        from django.core.management import execute_from_command_line
        os.makedirs(settings.APP_DATA_DIR)
        execute_from_command_line(['', 'migrate'])


def valid_date(s):
    try:
        if s.lower() in ['', 'n', 'none', 'null']:
            return None
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise ArgumentTypeError('Not a valid date: "{0}".'.format(s))


def _series(args):
    import series.functions
    if args.series_subparser == 'add':
        series.functions.series.create(args.name, args.link)
    elif args.series_subparser == 'edit':
        series_obj = series.functions.series.get.by_term(args.series)
        if series_obj:
            series.functions.series.edit(series_obj,
                                         args.series_edit_subparser,
                                         args.value)
    elif args.series_subparser == 'info':
        series_obj = series.functions.series.get.by_term(args.name)
        if series_obj:
            series.functions.series.info(series_obj)
    elif args.series_subparser == 'list':
        if args.search:
            series.functions.series.list.by_term(args.search)
        else:
            series.functions.series.list.all()
    else:
        series_parser.print_help()


def _runserver(args):
    from django.core.management import execute_from_command_line
    execute_from_command_line(['', 'runserver'])


def _load(args):
    import bindings.functions as bindings_functions
    import books.functions as books_functions
    import genres.functions as genres_functions
    import persons.functions as persons_functions
    import publishers.functions as publishers_functions
    import series.functions as series_functions
    with open(args.path, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())

    if 'books' in data:
        for b in data['books']:
            authors = []
            for a in b['authors']:
                person, created = persons_functions.person.create(
                    a['first_name'],
                    a['last_name'],
                    a['links']
                )
                authors.append(str(person.id))

            genres = []
            for g in b['genres']:
                genre, created = genres_functions.genre.create(g['name'])
                genres.append(str(genre.id))

            series, created = series_functions.series.create(
                b['series']['name'],
                b['series']['links']
            )
            book, created = books_functions.book.create(
                b['title'],
                authors,
                str(series.id),
                b['volume'],
                genres,
                b['links']
            )

            for e in b['editions']:
                binding, created = bindings_functions.binding.create(
                    e['binding']['name']
                )
                publisher, created = publishers_functions.publisher.create(
                    e['publisher']['name'],
                    e['publisher']['links']
                )
                edition, created = books_functions.edition.create(
                    book,
                    e['isbn'],
                    e['publishing_date'],
                    e['cover'],
                    str(binding.id),
                    str(publisher.id),
                    e['languages'],
                    e['files']
                )

                for a in e['acquisitions']:
                    if not edition.acquisitions.filter(date=a['date']). \
                            filter(price=a['price']).exists() and \
                            (a['date'] or a['price']):
                        acquisition = books_functions.edition.acquisition.add(
                            edition,
                            a['date'],
                            a['price']
                        )

                for r in e['reads']:
                    if not edition.reads.filter(started=r['started']). \
                            filter(finished=r['finished']).exists() and \
                            (r['started'] or r['finished']):
                        read = books_functions.edition.read.add(
                            edition,
                            r['started'],
                            r['finished']
                        )


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
    parser.add_argument('-v', '--version', action='version',
                        version=app_version(__app_name__, __description__,
                                            __version__, __license__,
                                            __author__, __email__))
    subparser = parser.add_subparsers(dest='subparser')

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
    series_parser = subparsers.add_parser('series', help=_('Manage series'))
    series_parser.set_defaults(func=_series)
    series_subparser = series_parser.add_subparsers(dest='series_subparser')

    # series add
    series_add_parser = series_subparser.add_parser('add',
                                                    help=_('Add a new series'))
    series_add_parser.add_argument('name', help='name')
    series_add_parser.add_argument('--link', nargs='*', default=[],
                                   help=_('Links'))

    # series edit
    series_edit_parser = series_subparser.add_parser(
        'edit',
        help=_('Edit a book edition'),
        prefix_chars='_'
    )
    series_edit_parser.add_argument('edition', help=_('Which edition to edit'))
    series_edit_subparser = series_edit_parser.add_subparsers(
        dest='series_edit_subparser',
        help=_('Which field to edit')
    )

    series_edit_name_parser = series_edit_subparser.add_parser('name')
    series_edit_name_parser.add_argument('value',
                                         help=_('New value for field'))

    series_edit_add_link_parser = series_edit_subparser.add_parser('+link')
    series_edit_add_link_parser.add_argument('value',
                                             help=_('New value for field'))

    series_edit_remove_link_parser = series_edit_subparser.add_parser('-link')
    series_edit_remove_link_parser.add_argument('value',
                                                help=_('New value for field'))

    series_edit_parser.add_argument('series', help=_('Which series to edit'))
    series_edit_parser.add_argument('field', choices=['name'],
                                    help=_('Field to edit'))
    series_edit_parser.add_argument('value', help=_('New value for field'))

    # series info
    series_info_parser = series_subparser.add_parser(
        'info',
        help=_('Show information of series')
    )
    series_info_parser.add_argument('name', help=_('Series name'))

    # series list
    series_list_parser = series_subparser.add_parser('list',
                                                     help=_('List series'))
    series_list_parser.add_argument('--search', help=_('Search by term'))


    # create the parser for the "runserver" subcommand
    runserver_parser = subparsers.add_parser('runserver',
                                             help=_('Start local http server'))
    runserver_parser.set_defaults(func=_runserver)


    # create the parser for the "load" subcommand
    load_parser = subparsers.add_parser('load', help='load data from json')
    load_parser.set_defaults(func=_load)
    load_parser.add_argument('path', help='path to json file')


    # create the parser for the "reading-list" subcommand
    reading_list_parser = subparsers.add_parser('reading-list', help=_('show reading-list'))
    reading_list_parser.set_defaults(func=_reading_list)
    reading_list_parser.add_argument('--limit', type=int, help='limit list to n entries')


    # create the parser for the "statistics" subcommand
    statistics_parser = subparsers.add_parser('statistics', help=_('show statistics'))
    statistics_parser.set_defaults(func=_statistics)


    args = parser.parse_args()
    if args.subparser:
        args.func(args)
    else:
        parser.print_usage()
