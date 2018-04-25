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


def _journal(args):
    import journals.functions
    if args.journal_subparser == 'add':
        journals.functions.journal.create(args.name, args.link)
    elif args.journal_subparser == 'edit':
        journal = journals.functions.journal.get.by_term(args.journal)
        if journal:
            journals.functions.journal.edit(journal, args.field, args.value)
    elif args.journal_subparser == 'info':
        journal = journals.functions.journal.get.by_term(args.journal)
        if journal:
            journals.functions.journal.info(journal)
    elif args.journal_subparser == 'list':
        if args.search:
            journals.functions.journal.list.by_term(args.search)
        else:
            journals.functions.journal.list.all()
    else:
        journal_parser.print_help()


def _magazine(args):
    import magazines.functions
    if args.magazine_subparser == 'add':
        magazines.functions.magazine.create(args.name, args.feed, args.link)
    elif args.magazine_subparser == 'delete':
        magazine = magazines.functions.magazine.get.by_term(args.magazine)
        if magazine:
            magazines.functions.magazine.delete(magazine)
    elif args.magazine_subparser == 'edit':
        magazine = magazines.functions.magazine.get.by_term(args.magazine)
        if magazine:
            magazines.functions.magazine.edit(magazine, args.field, args.value)
    elif args.magazine_subparser == 'info':
        magazine = magazines.functions.magazine.get.by_term(args.magazine)
        if magazine:
            magazines.functions.magazine.info(magazine)
    elif args.magazine_subparser == 'issue':
        magazine = magazines.functions.magazine.get.by_term(args.magazine)
        if args.magazine_issue_subparser == 'acquisition' and magazine:
            issue = magazines.functions.issue.get.by_term(magazine, args.issue)
            if args.magazine_issue_acquisition_subparser == 'add' and issue:
                magazines.functions.issue.acquisition.add(issue, args.date,
                                                          args.price)
            elif args.magazine_issue_acquisition_subparser == 'delete' and \
                    issue:
                magazines.functions.issue.acquisition.delete(issue,
                                                             args.acquisition)
            elif args.magazine_issue_acquisition_subparser == 'edit' and issue:
                magazines.functions.issue.acquisition.edit(
                    issue,
                    args.acquisition,
                    args.magazine_issue_acquisition_edit_subparser,
                    args.value
                )
        elif args.magazine_issue_subparser == 'add' and magazine:
            magazines.functions.issue.create(magazine, args.issue,
                                             args.publishing_date, args.cover,
                                             args.language, args.link,
                                             args.file)
        elif args.magazine_issue_subparser == 'edit' and magazine:
            issue = magazines.functions.issue.get.by_term(magazine, args.issue)
            if issue:
                magazines.functions.issue.edit(
                    issue,
                    args.magazine_issue_edit_subparser,
                    args.value
                )
        elif args.magazine_issue_subparser == 'info' and magazine:
            issue = magazines.functions.issue.get.by_term(magazine, args.issue)
            if issue:
                magazines.functions.issue.info(issue)
        elif args.magazine_issue_subparser == 'list' and magazine:
            if args.search:
                magazines.functions.issue.list.by_term(magazine, args.search)
            else:
                magazines.functions.issue.list.all(magazine)
        elif args.magazine_issue_subparser == 'read' and magazine:
            issue = magazines.functions.issue.get.by_term(magazine, args.issue)
            if args.magazine_issue_read_subparsers == 'add' and issue:
                magazines.functions.issue.read.add(issue, args.started,
                                                   args.finished)
            elif args.magazine_issue_read_subparsers == 'delete' and issue:
                magazines.functions.issue.read.delete(issue, args.read)
            elif args.magazine_issue_read_subparsers == 'edit' and issue:
                magazines.functions.issue.read.edit(issue, args.read,
                                                    args.field, args.value)
        else:
            magazine_issue_parser.print_help()
    elif args.magazine_subparser == 'list':
        if args.search:
            magazines.functions.magazine.list.by_term(args.search)
        else:
            magazines.functions.magazine.list.all()
    else:
        magazine_parser.print_help()


def _paper(args):
    import papers.functions
    if args.paper_subparser == 'acquisition':
        paper = papers.functions.paper.get.by_term(args.paper)
        if args.paper_acquisition_subparser == 'add' and paper:
            papers.functions.paper.acquisition.add(paper, args.date,
                                                   args.price)
        elif args.paper_acquisition_subparser == 'delete' and paper:
            papers.functions.paper.acquisition.delete(paper, args.acquisition)
        elif args.paper_acquisition_subparser == 'edit' and paper:
            papers.functions.paper.acquisition.edit(
                paper,
                args.acquisition,
                args.paper_acquisition_edit_subparser,
                args.value
            )
    elif args.paper_subparser == 'add':
        papers.functions.paper.create(args.title, args.author,
                                      args.publishing_date, args.journal,
                                      args.volume, args.language, args.link)
    elif args.paper_subparser == 'edit':
        paper = papers.functions.paper.get.by_term(args.paper)
        if paper:
            papers.functions.paper.edit(paper, args.paper_edit_subparser,
                                        args.value)
    elif args.paper_subparser == 'list':
        if args.shelf:
            papers.functions.paper.list.by_shelf(args.shelf)
        elif args.search:
            papers.functions.paper.list.by_term(args.search)
        else:
            papers.functions.paper.list.all()
    elif args.paper_subparser == 'info':
        paper = papers.functions.paper.get.by_term(args.paper)
        if paper:
            papers.functions.paper.info(paper)
    elif args.paper_subparser == 'open':
        paper = papers.functions.paper.get.by_term(args.paper)
        if paper:
            file = paper.files.get(pk=args.file)
            path = os.path.join(settings.MEDIA_ROOT, file.file.path)
            if sys.platform == 'linux':
                os.system('xdg-open "%s"' % path)
            else:
                os.system('open "%s"' % path)
    elif args.paper_subparser == 'parse':
        papers.functions.paper.parse.from_bibtex(args.bibtex, args.file)
    elif args.paper_subparser == 'read':
        paper = papers.functions.paper.get.by_term(args.paper)
        if args.paper_read_subparsers == 'add' and paper:
            papers.functions.paper.read.add(paper, args.started,
                                            args.finished)
        elif args.paper_read_subparsers == 'delete' and paper:
            papers.functions.paper.read.delete(paper, args.read)
        elif args.paper_read_subparsers == 'edit' and paper:
            papers.functions.paper.read.edit(paper, args.read, args.field,
                                             args.value)
    else:
        paper_parser.print_help()


def _person(args):
    import persons.functions
    if args.person_subparser == 'add':
        persons.functions.person.create(args.first_name, args.last_name,
                                        args.link)
    elif args.person_subparser == 'edit':
        person = persons.functions.person.get.by_term(args.person)
        if person:
            persons.functions.person.edit(person, args.field, args.value)
    elif args.person_subparser == 'info':
        person = persons.functions.person.get.by_term(args.person)
        if person:
            persons.functions.person.info(person)
    elif args.person_subparser == 'list':
        if args.search:
            persons.functions.person.list.by_term(args.search)
        else:
            persons.functions.person.list.all()
    else:
        person_parser.print_help()


def _publisher(args):
    import publishers.functions
    if args.publisher_subparser == 'add':
        publishers.functions.publisher.create(args.name, args.link)
    elif args.publisher_subparser == 'edit':
        publisher = publishers.functions.publisher.get.by_term(args.publisher)
        if publisher:
            publishers.functions.publisher.edit(publisher,
                                                args.publisher_edit_subparser,
                                                args.value)
    elif args.publisher_subparser == 'info':
        publisher = publishers.functions.publisher.get.by_term(args.publisher)
        if publisher:
            publishers.functions.publisher.info(publisher)
    elif args.publisher_subparser == 'list':
        if args.search:
            publishers.functions.publisher.list.by_term(args.search)
        else:
            publishers.functions.publisher.list.all()
    else:
        publisher_parser.print_help()


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
    subparsers = parser.add_subparsers(dest='subparser')

    # create the parser for the "binding" subcommand
    bindings.argparse.add_subparser(subparsers)

    # create the parser for the "book" subcommand
    books.argparse.add_subparser(subparsers)

    # create the parser for the "genre" subcommand
    genres.argparse.add_subparser(subparsers)


    # create the parser for the "journal" subcommand
    journal_parser = subparsers.add_parser('journal', help='manage journals')
    journal_parser.set_defaults(func=_journal)
    journal_subparser = journal_parser.add_subparsers(dest='journal_subparser')

    # journal add
    journal_add_parser = journal_subparser.add_parser('add', help='add a journal')
    journal_add_parser.add_argument('name', help='name')
    journal_add_parser.add_argument('--link', nargs='*', default=[], help='links')

    # journal edit
    journal_edit_parser = journal_subparser.add_parser('edit', help='edit a journal')
    journal_edit_parser.add_argument('journal', help='which journal to edit')
    journal_edit_parser.add_argument('field', choices=['name'], help='which field to edit')
    journal_edit_parser.add_argument('value', help='new value for field')

    # journal info
    journal_info_parser = journal_subparser.add_parser('info', help='show information of a journal')
    journal_info_parser.add_argument('journal', help='of which journal to show information')

    # journal list
    journal_list_parser = journal_subparser.add_parser('list', help='list journals')
    journal_list_parser.add_argument('--search', help='filter by term')


    # create the parser for the "magazine" subcommand
    magazine_parser = subparsers.add_parser('magazine', help='manage magazines')
    magazine_parser.set_defaults(func=_magazine)
    magazine_subparser = magazine_parser.add_subparsers(dest='magazine_subparser')

    # magazine add
    magazine_add_parser = magazine_subparser.add_parser('add', help='add a magazine')
    magazine_add_parser.add_argument('name', help='name')
    magazine_add_parser.add_argument('--feed', help='feed url')
    magazine_add_parser.add_argument('--link', nargs='*', default=[], help='links')

    # magazine delete
    magazine_delete_parser = magazine_subparser.add_parser('delete', help='delete a magazine')
    magazine_delete_parser.add_argument('magazine', help='which magazine')

    # magazine edit
    magazine_edit_parser = magazine_subparser.add_parser('edit', help='edit a magazine')
    magazine_edit_parser.add_argument('magazine', help='which magazine to edit')
    magazine_edit_parser.add_argument('field', choices=['name', 'feed'], help='which field to edit')
    magazine_edit_parser.add_argument('value', help='new value for field')

    # magazine info
    magazine_info_parser = magazine_subparser.add_parser('info', help='show information of a magazine')
    magazine_info_parser.add_argument('magazine', help='of which magazine to show information')

    # magazine issue
    magazine_issue_parser = magazine_subparser.add_parser('issue', help='manage issues of a magazine')
    magazine_issue_parser.add_argument('magazine', help='issues of which magazine')
    magazine_issue_subparser = magazine_issue_parser.add_subparsers(dest='magazine_issue_subparser')

    # magazine issue acquisitions
    magazine_issue_acquisition_parser = magazine_issue_subparser.add_parser('acquisition', help='manage acquisition of a magazine issue')
    magazine_issue_acquisition_parser.add_argument('issue', help='of which issue to manage an acquisition')
    magazine_issue_acquisition_subparser = magazine_issue_acquisition_parser.add_subparsers(dest='magazine_issue_acquisition_subparser')

    magazine_issue_acquisition_add_parser = magazine_issue_acquisition_subparser.add_parser('add', help='add an acquisition')
    magazine_issue_acquisition_add_parser.add_argument('--date', default=None, type=valid_date, help='date')
    magazine_issue_acquisition_add_parser.add_argument('--price', default=0, type=float, help='price')

    magazine_issue_acquisition_delete_parser = magazine_issue_acquisition_subparser.add_parser('delete', help='delete an acquisition')
    magazine_issue_acquisition_delete_parser.add_argument('acquisition', type=int, help='which acquisition to delete')

    magazine_issue_acquisition_edit_parser = magazine_issue_acquisition_subparser.add_parser('edit', help='edit an acquisition')
    magazine_issue_acquisition_edit_parser.add_argument('acquisition', type=int, help='which acquisition to edit')

    magazine_issue_acquisition_edit_subparser = magazine_issue_acquisition_edit_parser.add_subparsers(dest='magazine_issue_acquisition_edit_subparser', help='which field to edit')
    magazine_issue_acquisition_edit_date_parser = magazine_issue_acquisition_edit_subparser.add_parser('date')
    magazine_issue_acquisition_edit_date_parser.add_argument('value', type=valid_date, help='new value for field')

    magazine_issue_acquisition_edit_price_parser = magazine_issue_acquisition_edit_subparser.add_parser('price')
    magazine_issue_acquisition_edit_price_parser.add_argument('value', type=float, help='new value for field')

    # magazine issue add
    magazine_issue_add_parser = magazine_issue_subparser.add_parser('add', help='add an issue to a magazine')
    magazine_issue_add_parser.add_argument('issue', help='issue')
    magazine_issue_add_parser.add_argument('--publishing-date', type=valid_date, help='Publishing date')
    magazine_issue_add_parser.add_argument('--cover', help='path to a cover image')
    magazine_issue_add_parser.add_argument('--language', nargs='*', default=[], help='languages')
    magazine_issue_add_parser.add_argument('--link', nargs='*', default=[], help='links')
    magazine_issue_add_parser.add_argument('--file', nargs='*', default=[], help='files')

    # magazine issue edit
    magazine_issue_edit_parser = magazine_issue_subparser.add_parser('edit', help='edit a magazine issue')
    magazine_issue_edit_parser.add_argument('issue', help='which issue to edit')
    magazine_issue_edit_subparser = magazine_issue_edit_parser.add_subparsers(dest='magazine_issue_edit_subparser', help='which field to edit')

    magazine_issue_edit_issue_parser = magazine_issue_edit_subparser.add_parser('issue')
    magazine_issue_edit_issue_parser.add_argument('value', help='new value for field')

    magazine_issue_edit_published_parser = magazine_issue_edit_subparser.add_parser('publishing-date')
    magazine_issue_edit_published_parser.add_argument('value', type=valid_date, help='new value for field')

    magazine_issue_edit_cover_parser = magazine_issue_edit_subparser.add_parser('cover')
    magazine_issue_edit_cover_parser.add_argument('value', help='new value for field')

    magazine_issue_edit_add_language_parser = magazine_issue_edit_subparser.add_parser('+language')
    magazine_issue_edit_add_language_parser.add_argument('value', help='new value for field')

    magazine_issue_edit_remove_language_parser = magazine_issue_edit_subparser.add_parser('-language')
    magazine_issue_edit_remove_language_parser.add_argument('value', help='new value for field')

    magazine_issue_edit_add_link_parser = magazine_issue_edit_subparser.add_parser('+link')
    magazine_issue_edit_add_link_parser.add_argument('value', help='new value for field')

    magazine_issue_edit_remove_link_parser = magazine_issue_edit_subparser.add_parser('-link')
    magazine_issue_edit_remove_link_parser.add_argument('value', help='new value for field')

    magazine_issue_edit_add_file_parser = magazine_issue_edit_subparser.add_parser('+file')
    magazine_issue_edit_add_file_parser.add_argument('value', help='new value for field')

    # magazine issue info
    magazine_issue_info_parser = magazine_issue_subparser.add_parser('info', help='show information of a magazine issue')
    magazine_issue_info_parser.add_argument('issue', help='of which issue to show information')

    # magazine issue list
    magazine_issue_list_parser = magazine_issue_subparser.add_parser('list', help='list issues of a magazine')
    magazine_issue_list_parser.add_argument('--shelf', choices=['read', 'unread'], help='filter on shelves')
    magazine_issue_list_parser.add_argument('--search', help='search by term')

    # magazine issue reads
    magazine_issue_read_parser = magazine_issue_subparser.add_parser('read', help='manage read of papers')
    magazine_issue_read_parser.add_argument('issue', help='of which issue to manage a read')
    magazine_issue_read_subparsers = magazine_issue_read_parser.add_subparsers(dest='magazine_issue_read_subparsers')

    magazine_issue_read_add_parser = magazine_issue_read_subparsers.add_parser('add', help='add a read')
    magazine_issue_read_add_parser.add_argument('--started', default=None, type=valid_date, help='date started')
    magazine_issue_read_add_parser.add_argument('--finished', default=None, type=valid_date, help='date finished')

    magazine_issue_read_delete_parser = magazine_issue_read_subparsers.add_parser('delete', help='delete a read')
    magazine_issue_read_delete_parser.add_argument('read', type=int, help='which read to delete')

    magazine_issue_read_edit_parser = magazine_issue_read_subparsers.add_parser('edit', help='edit a read')
    magazine_issue_read_edit_parser.add_argument('read', type=int, help='which read to edit')
    magazine_issue_read_edit_parser.add_argument('field', choices=['started', 'finished'], help='which field to edit')
    magazine_issue_read_edit_parser.add_argument('value', type=valid_date, help='new value for field')

    # magazine list
    magazine_list_parser = magazine_subparser.add_parser('list', help='list magazines')
    magazine_list_parser.add_argument('--search', help='search by term')


    # create the parser for the "paper" subcommand
    paper_parser = subparsers.add_parser('paper', help='manage papers')
    paper_parser.set_defaults(func=_paper)
    paper_subparser = paper_parser.add_subparsers(dest='paper_subparser')

    # paper acquisitions
    paper_acquisition_parser = paper_subparser.add_parser('acquisition', help='manage acquisition of a paper')
    paper_acquisition_parser.add_argument('paper', help='of which paper to manage an acquisition')
    paper_acquisition_subparser = paper_acquisition_parser.add_subparsers(dest='paper_acquisition_subparser')

    paper_acquisition_add_parser = paper_acquisition_subparser.add_parser('add', help='add an acquisition')
    paper_acquisition_add_parser.add_argument('--date', default=None, type=valid_date, help='date')
    paper_acquisition_add_parser.add_argument('--price', default=0, type=float, help='price')

    paper_acquisition_delete_parser = paper_acquisition_subparser.add_parser('delete', help='delete an acquisition')
    paper_acquisition_delete_parser.add_argument('acquisition', type=int, help='which acquisition to delete')

    paper_acquisition_edit_parser = paper_acquisition_subparser.add_parser('edit', help='edit an acquisition')
    paper_acquisition_edit_parser.add_argument('acquisition', type=int, help='which acquisition to edit')

    paper_acquisition_edit_subparser = paper_acquisition_edit_parser.add_subparsers(dest='paper_acquisition_edit_subparser', help='which field to edit')
    paper_acquisition_edit_date_parser = paper_acquisition_edit_subparser.add_parser('date')
    paper_acquisition_edit_date_parser.add_argument('value', type=valid_date, help='new value for field')

    paper_acquisition_edit_price_parser = paper_acquisition_edit_subparser.add_parser('price')
    paper_acquisition_edit_price_parser.add_argument('value', type=float, help='new value for field')

    # paper add
    paper_add_parser = paper_subparser.add_parser('add', help='add a paper')
    paper_add_parser.add_argument('title', help='title')
    paper_add_parser.add_argument('--author', nargs='*', default=[], help='authors')
    paper_add_parser.add_argument('--publishing-date', type=valid_date, help='Publishing date')
    paper_add_parser.add_argument('--journal', help='journal')
    paper_add_parser.add_argument('--volume', help='journal volume')
    paper_add_parser.add_argument('--language', nargs='*', default=[], help='languages')
    paper_add_parser.add_argument('--link', nargs='*', default=[], help='links')

    # paper edit
    paper_edit_parser = paper_subparser.add_parser('edit', help='edit a paper', prefix_chars='_')
    paper_edit_parser.add_argument('paper', help='which paper to edit')
    paper_edit_subparser = paper_edit_parser.add_subparsers(dest='paper_edit_subparser', help='which field to edit')

    paper_edit_title_parser = paper_edit_subparser.add_parser('title')
    paper_edit_title_parser.add_argument('value', help='new value for field')

    paper_edit_published_parser = paper_edit_subparser.add_parser('publishing-date')
    paper_edit_published_parser.add_argument('value', type=valid_date, help='new value for field')

    paper_edit_journal_parser = paper_edit_subparser.add_parser('journal')
    paper_edit_journal_parser.add_argument('value', help='new value for field')

    paper_edit_volume_parser = paper_edit_subparser.add_parser('volume')
    paper_edit_volume_parser.add_argument('value', help='new value for field')

    paper_edit_add_language_parser = paper_edit_subparser.add_parser('+language')
    paper_edit_add_language_parser.add_argument('value', help='new value for field')

    paper_edit_remove_language_parser = paper_edit_subparser.add_parser('-language')
    paper_edit_remove_language_parser.add_argument('value', help='new value for field')

    paper_edit_add_link_parser = paper_edit_subparser.add_parser('+link')
    paper_edit_add_link_parser.add_argument('value', help='new value for field')

    paper_edit_add_file_parser = paper_edit_subparser.add_parser('+file')
    paper_edit_add_file_parser.add_argument('value', help='new value for field')

    # paper list
    paper_list_parser = paper_subparser.add_parser('list', help='list papers')
    paper_list_parser.add_argument('--shelf', choices=['read', 'unread'], nargs='?', help='filter on shelves')
    paper_list_parser.add_argument('--search', help='search by term')

    # paper info
    paper_info_parser = paper_subparser.add_parser('info', help='show information of a paper')
    paper_info_parser.add_argument('paper', help='of which paper to show information')

    # paper open
    paper_open_parser = paper_subparser.add_parser('open', help='open a file of a paper')
    paper_open_parser.add_argument('paper', nargs='?', help='which paper')
    paper_open_parser.add_argument('file', type=int, help='which file to open')

    # paper parse
    paper_parse_parser = paper_subparser.add_parser('parse', help='parse bibtex and add papers')
    paper_parse_parser.add_argument('bibtex', help='bibtex file')
    paper_parse_parser.add_argument('-f', '--file', nargs='*', default=[], help='files')

    # paper reads
    paper_read_parser = paper_subparser.add_parser('read', help='manage read of papers')
    paper_read_parser.add_argument('paper', help='of which paper to manage a read')
    paper_read_subparsers = paper_read_parser.add_subparsers(dest='paper_read_subparsers')

    paper_read_add_parser = paper_read_subparsers.add_parser('add', help='add a read')
    paper_read_add_parser.add_argument('--started', default=None, type=valid_date, help='date started')
    paper_read_add_parser.add_argument('--finished', default=None, type=valid_date, help='date finished')

    paper_read_delete_parser = paper_read_subparsers.add_parser('delete', help='delete a read')
    paper_read_delete_parser.add_argument('read', type=int, help='which read to delete')

    paper_read_edit_parser = paper_read_subparsers.add_parser('edit', help='edit a read')
    paper_read_edit_parser.add_argument('read', type=int, help='which read to edit')
    paper_read_edit_parser.add_argument('field', choices=['started', 'finished'], help='which field to edit')
    paper_read_edit_parser.add_argument('value', type=valid_date, help='new value for field')


    # create the parser for the "person" subcommand
    person_parser = subparsers.add_parser('person', help='manage persons')
    person_parser.set_defaults(func=_person)
    person_subparser = person_parser.add_subparsers(dest='person_subparser')

    # person add
    person_add_parser = person_subparser.add_parser('add', help='add a person')
    person_add_parser.add_argument('first_name', help='first name')
    person_add_parser.add_argument('last_name', help='last name')
    person_add_parser.add_argument('--link', nargs='*', default=[], help='links')

    # person edit
    person_edit_parser = person_subparser.add_parser('edit', help='edit a person')
    person_edit_parser.add_argument('person', help='which person to edit')
    person_edit_parser.add_argument('field', choices=['first_name', 'last_name'], help='field to edit')
    person_edit_parser.add_argument('value', help='new value for field')

    # person info
    person_info_parser = person_subparser.add_parser('info', help='show information of a person')
    person_info_parser.add_argument('person', help='of which person to show information')

    # person list
    person_list_parser = person_subparser.add_parser('list', help='list persons')
    person_list_parser.add_argument('--search', help='search by term')


    # create the parser for the "publisher" subcommand
    publisher_parser = subparsers.add_parser('publisher', help='manage publishers')
    publisher_parser.set_defaults(func=_publisher)
    publisher_subparser = publisher_parser.add_subparsers(dest='publisher_subparser')

    # publisher add
    publisher_add_parser = publisher_subparser.add_parser('add', help='add a publisher')
    publisher_add_parser.add_argument('name', help='name')
    publisher_add_parser.add_argument('--link', nargs='*', default=[], help='links')

    # publisher edit
    publisher_edit_parser = publisher_subparser.add_parser('edit', help='edit a book publisher', prefix_chars='_')
    publisher_edit_parser.add_argument('publisher', help='which publisher to edit')
    publisher_edit_subparser = publisher_edit_parser.add_subparsers(dest='publisher_edit_subparser', help='which field to edit')

    publisher_edit_name_parser = publisher_edit_subparser.add_parser('name')
    publisher_edit_name_parser.add_argument('value', help='new value for field')

    publisher_edit_add_link_parser = publisher_edit_subparser.add_parser('+link')
    publisher_edit_add_link_parser.add_argument('value', help='new value for field')

    publisher_edit_remove_link_parser = publisher_edit_subparser.add_parser('-link')
    publisher_edit_remove_link_parser.add_argument('value', help='new value for field')

    # publisher info
    publisher_info_parser = publisher_subparser.add_parser('info', help='show information of a publisher')
    publisher_info_parser.add_argument('publisher', help='of which publisher to show information')

    # publisher list
    publisher_list_parser = publisher_subparser.add_parser('list', help='list publishers')
    publisher_list_parser.add_argument('--search', help='search by term')


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
