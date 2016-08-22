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
    if settings.DEVELOPMENT:
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


def _book(args):
    import books.functions
    if args.book_subparsers == 'add':
        books.functions.book.create(args.title, args.author, args.series, args.volume, args.link)
    elif args.book_subparsers == 'edit':
        book = books.functions.book.get.by_term(args.title)
        if book:
            books.functions.book.edit(book, args.field, args.value)
    elif args.book_subparsers == 'info':
        book = books.functions.book.get.by_term(args.title)
        if book:
            books.functions.book.info(book)
    elif args.book_subparsers == 'list':
        if args.shelf:
            books.functions.book.list.by_shelf(args.shelf)
        elif args.search:
            books.functions.book.list.by_term(args.search)
        else:
            books.functions.book.list.all()
    else:
        book_parser.print_help()


def _journal(args):
    import journals.functions
    if args.journal_subparsers == 'add':
        journals.functions.journal.create(args.name, args.link)
    elif args.journal_subparsers == 'edit':
        journal = journals.functions.journal.get.by_term(args.name)
        if journal:
            journals.functions.journal.edit(journal, args.field, args.value)
    elif args.journal_subparsers == 'info':
        journal = journals.functions.journal.get.by_term(args.name)
        if journal:
            journals.functions.journal.info(journal)
    elif args.journal_subparsers == 'list':
        if args.shelf:
            journals.functions.journal.list.by_shelf(args.shelf)
        elif args.search:
            journals.functions.journal.list.by_term(args.search)
        else:
            journals.functions.journal.list.all()
    else:
        journal_parser.print_help()


def _magazine(args):
    import magazines.functions
    if args.magazine_subparsers == 'add':
        magazines.functions.magazine.create(args.name, args.feed, args.link)
    elif args.magazine_subparsers == 'edit':
        magazine = magazines.functions.magazine.get(args.magazine)
        if magazine:
            magazines.functions.magazine.edit(magazine, args.field, args.value)
    elif args.magazine_subparsers == 'list':
        if args.search:
            magazines.functions.magazine.list.by_search(args.search)
        else:
            magazines.functions.magazine.list.all()
    elif args.magazine_subparsers == 'issue':
        magazine = magazines.functions.magazine.get.by_term(args.magazine)
        if args.magazine_issue_subparsers == 'acquisition' and magazine:
            issue = magazines.functions.issue.get.by_term(magazine, args.issue)
            if args.magazine_issue_acquisition_subparsers == 'add' and issue:
                magazines.functions.issue.acquisition.add(issue, args.date, args.price)
            elif args.magazine_issue_acquisition_subparsers == 'delete' and issue:
                magazines.functions.issue.acquisition.delete(issue, args.id)
            elif args.magazine_issue_acquisition_subparsers == 'edit' and issue:
                magazines.functions.issue.acquisition.edit(issue, args.id, args.magazine_issue_acquisition_edit_subparsers, args.value)
        elif args.magazine_issue_subparsers == 'add' and magazine:
            magazines.functions.issue.create(magazine, args.issue, args.published_on, args.cover, args.link, args.file)
        elif args.magazine_issue_subparsers == 'edit' and magazine:
            issue = magazines.functions.issue.get.by_term(magazine, args.issue)
            if issue:
                magazines.functions.issue.edit(issue, args.field, args.value)
        elif args.magazine_issue_subparsers == 'info' and magazine:
            issue = magazines.functions.issue.get.by_term(magazine, args.issue)
            if issue:
                magazines.functions.issue.info(issue)
        elif args.magazine_issue_subparsers == 'list' and magazine:
            magazines.functions.issue.list.all(magazine)
        elif args.magazine_issue_subparsers == 'read' and magazine:
            issue = magazines.functions.issue.get.by_term(magazine, args.issue)
            if args.magazine_issue_acquisition_subparsers == 'add' and issue:
                magazines.functions.issue.read.add(issue, args.started, args.finished)
            elif args.magazine_issue_acquisition_subparsers == 'delete' and issue:
                magazines.functions.issue.read.delete(issue, args.id)
            elif args.magazine_issue_acquisition_subparsers == 'edit' and issue:
                magazines.functions.issue.read.edit(issue, args.id, args.field, args.value)
        else:
            magazine_issue_parser.print_help()
    elif args.magazine_subparsers == 'info':
        magazine = magazines.functions.magazine.get.by_term(args.magazine)
        if magazine:
            magazines.functions.magazine.info(magazine)
    else:
        magazine_parser.print_help()


def _person(args):
    import persons.functions
    if args.person_subparsers == 'add':
        persons.functions.person.create(args.first_name, args.last_name)
    elif args.person_subparsers == 'edit':
        person = persons.functions.person.get.by_term(args.person)
        if person:
            persons.functions.person.edit(person, args.field, args.value)
    elif args.person_subparsers == 'info':
        person = persons.functions.person.get.by_term(args.person)
        if person:
            persons.functions.person.info(person)
    elif args.person_subparsers == 'list':
        if args.search:
            persons.functions.person.list.by_term(args.search)
        else:
            persons.functions.person.list.all()
    else:
        person_parser.print_help()


def _paper(args):
    import papers.functions
    if args.paper_subparsers == 'acquisition':
        paper = papers.functions.paper.get.by_term(args.paper)
        if args.paper_acquisition_subparsers == 'add' and paper:
            papers.functions.paper.acquisition.add(paper, args.date, args.price)
        elif args.paper_acquisition_subparsers == 'delete' and paper:
            papers.functions.paper.acquisition.delete(paper, args.id)
        elif args.paper_acquisition_subparsers == 'edit' and paper:
            papers.functions.paper.acquisition.edit(paper, args.id, args.paper_acquisition_edit_subparsers, args.value)
    elif args.paper_subparsers == 'create':
        papers.functions.paper.create(args.title, args.published_on, args.journal, args.volume)
    elif args.paper_subparsers == 'edit':
        paper = papers.functions.paper.get.by_term(args.paper)
        if paper:
            papers.functions.paper.edit(paper, args.field, args.value)
    elif args.paper_subparsers == 'list':
        if args.shelf:
            papers.functions.paper.list.by_shelf(args.shelf)
        elif args.search:
            papers.functions.paper.list.by_term(args.search)
        else:
            papers.functions.paper.list.all()
    elif args.paper_subparsers == 'info':
        paper = papers.functions.paper.get.by_term(args.paper)
        if paper:
            papers.functions.paper.info(paper)
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
        papers.functions.paper.parse.from_bibtex(args.bibtex, args.file)
    elif args.paper_subparsers == 'read':
        paper = papers.functions.paper.get.by_term(args.paper)
        if args.paper_read_subparsers == 'add' and paper:
            papers.functions.paper.read.add(paper, args.started, args.finished)
        elif args.paper_read_subparsers == 'delete' and paper:
            papers.functions.paper.read.delete(paper, args.id)
        elif args.paper_read_subparsers == 'edit' and paper:
            papers.functions.paper.read.edit(paper, args.id, args.field, args.value)
    else:
        paper_parser.print_help()


def _publisher(args):
    import publishers.functions
    if args.publisher_subparsers == 'add':
        publishers.functions.publisher.create(args.name, args.link)
    elif args.publisher_subparsers == 'edit':
        publisher = publishers.functions.publisher.get.by_term(args.publisher)
        if publisher:
            publishers.functions.publisher.edit(publisher, args.field, args.value)
    elif args.publisher_subparsers == 'info':
        publisher = publishers.functions.publisher.get.by_term(args.publisher)
        if publisher:
            publishers.functions.publisher.info(publisher)
    elif args.publisher_subparsers == 'list':
        if args.search:
            publishers.functions.publisher.list.by_term(args.search)
        else:
            publishers.functions.publisher.list.all()
    else:
        publisher_parser.print_help()


def _series(args):
    import series.functions
    if args.series_subparsers == 'add':
        series.functions.series.create(args.name)
    elif args.series_subparsers == 'edit':
        series_obj = series.functions.series.get.by_term(args.series)
        if series_obj:
            series.functions.series.edit(series_obj, args.field, args.value)
    elif args.series_subparsers == 'info':
        series_obj = series.functions.series.get.by_term(args.series)
        if series_obj:
            series.functions.series.info(series_obj)
    elif args.series_subparsers == 'list':
        if args.search:
            series.functions.series.list.by_term(args.search)
        else:
            series.functions.series.list.all()
    else:
        series_parser.print_help()


def _runserver(args):
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    init()


    parser = ArgumentParser(prog=settings.APP_NAME, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version=settings.APP_VERSION)
    subparsers = parser.add_subparsers(dest='subparser')


    # create the parser for the "book" subcommand
    book_parser = subparsers.add_parser('book', help='subcommand for books')
    book_parser.set_defaults(func=_book)
    book_subparsers = book_parser.add_subparsers(dest='book_subparsers')

    # book add
    book_add_parser = book_subparsers.add_parser('add', help='add a book')
    book_add_parser.add_argument('name', help='book name')
    book_add_parser.add_argument('-a', '--auhtor', nargs='*', default=[], type=int, help='authors')
    book_add_parser.add_argument('-s', '--series', default=None, type=int, help='series')
    book_add_parser.add_argument('-v', '--volume', default=None, type=float, help='series volume')
    book_add_parser.add_argument('-l', '--link', nargs='*', default=[], help='links')

    # book edit
    book_edit_parser = book_subparsers.add_parser('edit', help='edit a book')
    book_edit_parser.add_argument('book', help='which book to edit')
    book_edit_parser.add_argument('field', choices=['name'], help='field to edit')
    book_edit_parser.add_argument('value', help='new value for field')

    # book info
    book_info_parser = book_subparsers.add_parser('info', help='show information of book')
    book_info_parser.add_argument('name', help='book name')

    # book list
    book_list_parser = book_subparsers.add_parser('list', help='list books')
    book_list_parser.add_argument('-shelf', choices=['read', 'unread'], help='filter on shelves')
    book_list_parser.add_argument('-s', '--search', help='filter on shelves')


    # create the parser for the "journal" subcommand
    journal_parser = subparsers.add_parser('journal', help='subcommand for journals')
    journal_parser.set_defaults(func=_journal)
    journal_subparsers = journal_parser.add_subparsers(dest='journal_subparsers')

    # journal add
    journal_add_parser = journal_subparsers.add_parser('add', help='add a journal')
    journal_add_parser.add_argument('name', help='journal name')
    journal_add_parser.add_argument('-l', '--link', nargs='*', default=[], help='journal links')

    # journal edit
    journal_edit_parser = journal_subparsers.add_parser('edit', help='edit a journal')
    journal_edit_parser.add_argument('journal', help='which journal to edit')
    journal_edit_parser.add_argument('field', choices=['name'], help='field to edit')
    journal_edit_parser.add_argument('value', help='new value for field')

    # journal info
    journal_info_parser = journal_subparsers.add_parser('info', help='show information of journal')
    journal_info_parser.add_argument('name', help='journal name')

    # journal list
    journal_list_parser = journal_subparsers.add_parser('list', help='list journals')
    journal_list_parser.add_argument('-shelf', choices=['read', 'unread'], help='filter on shelves')
    journal_list_parser.add_argument('-s', '--search', help='filter on shelves')


    # create the parser for the "magazine" subcommand
    magazine_parser = subparsers.add_parser('magazine', help='subcommand for local http server')
    magazine_parser.set_defaults(func=_magazine)
    magazine_subparsers = magazine_parser.add_subparsers(dest='magazine_subparsers')

    # magazine add
    magazine_add_parser = magazine_subparsers.add_parser('add', help='add a magazine')
    magazine_add_parser.add_argument('name', help='magazine name')
    magazine_add_parser.add_argument('-f', '--feed', help='magazine feed url')
    magazine_add_parser.add_argument('-l', '--link', nargs='*', default=[], help='magazine links')

    # magazine edit
    magazine_edit_parser = magazine_subparsers.add_parser('edit', help='edit a magazine')
    magazine_edit_subparser = magazine_edit_parser.add_subparsers(dest='magazine_edit_subparsers', help='which field to edit')

    magazine_edit_name_parser = magazine_edit_subparser.add_parser('name')
    magazine_edit_name_parser.add_argument('value', help='new value for name field')

    magazine_edit_feed_parser = magazine_edit_subparser.add_parser('feed')
    magazine_edit_feed_parser.add_argument('value', help='new value for feed field')

    # magazine info
    magazine_info_parser = magazine_subparsers.add_parser('info', help='show information of a magazine')
    magazine_info_parser.add_argument('magazine', help='magazine name')

    # magazine issue
    magazine_issue_parser = magazine_subparsers.add_parser('issue', help='issues of a magazine')
    magazine_issue_parser.add_argument('magazine', help='issues of which magazine')
    magazine_issue_subparsers = magazine_issue_parser.add_subparsers(dest='magazine_issue_subparsers')

    # magazine issue acquisitions
    magazine_issue_acquisition_parser = magazine_issue_subparsers.add_parser('acquisition', help='manage acquisition of magazine issues')
    magazine_issue_acquisition_parser.add_argument('issue', help='of which issue to manage an acquisition')
    magazine_issue_acquisition_subparsers = magazine_issue_acquisition_parser.add_subparsers(dest='magazine_issue_acquisition_subparsers')

    magazine_issue_acquisition_add_parser = magazine_issue_acquisition_subparsers.add_parser('add', help='manage additions of acquisitions')
    magazine_issue_acquisition_add_parser.add_argument('-date', default=None, type=valid_date, help='date')
    magazine_issue_acquisition_add_parser.add_argument('-price', default=0, type=float, help='price')

    magazine_issue_acquisition_edit_parser = magazine_issue_acquisition_subparsers.add_parser('edit', help='manage edition of acquisitions')
    magazine_issue_acquisition_edit_parser.add_argument('id', type=int, help='which acquisition to edit')

    magazine_issue_acquisition_edit_subparser = magazine_issue_acquisition_edit_parser.add_subparsers(dest='magazine_issue_acquisition_edit_subparsers', help='which field to edit')
    magazine_issue_acquisition_edit_date_parser = magazine_issue_acquisition_edit_subparser.add_parser('date')
    magazine_issue_acquisition_edit_date_parser.add_argument('value', type=str, help='new value for field')

    magazine_issue_acquisition_edit_price_parser = magazine_issue_acquisition_edit_subparser.add_parser('price')
    magazine_issue_acquisition_edit_price_parser.add_argument('value', type=valid_date, help='new value for field')

    magazine_issue_acquisition_delete_parser = magazine_issue_acquisition_subparsers.add_parser('delete', help='manage deletion of acquisitions')
    magazine_issue_acquisition_delete_parser.add_argument('id', type=int, help='which acquisition to delete')

    # magazine issue add
    magazine_issue_add_parser = magazine_issue_subparsers.add_parser('add', help='add an issue to a magazine')
    magazine_issue_add_parser.add_argument('issue', help='issue')
    magazine_issue_add_parser.add_argument('-p', '--published_on', type=valid_date, help='issue published on')
    magazine_issue_add_parser.add_argument('-c', '--cover', help='path to a cover image')
    magazine_issue_add_parser.add_argument('-l', '--link', nargs='*', default=[], help='links to add to issue')
    magazine_issue_add_parser.add_argument('-f', '--file', nargs='*', default=[], help='files to add to issue')

    # magazine issue edit
    magazine_issue_edit_parser = magazine_issue_subparsers.add_parser('edit', help='edit an issue of a magazine')
    magazine_issue_edit_parser.add_argument('issue', type=int, help='which issue to edit')

    magazine_issue_edit_subparser = magazine_issue_edit_parser.add_subparsers(dest='magazine_issue_edit_subparsers', help='which field to edit')
    magazine_issue_edit_issue_parser = magazine_issue_edit_subparser.add_parser('issue')
    magazine_issue_edit_issue_parser.add_argument('value', help='new value for field')

    magazine_issue_edit_published_on_parser = magazine_issue_edit_subparser.add_parser('published_on')
    magazine_issue_edit_published_on_parser.add_argument('value', type=valid_date, help='new value for field')

    magazine_issue_edit_cover_parser = magazine_issue_edit_subparser.add_parser('cover')
    magazine_issue_edit_cover_parser.add_argument('value', help='new value for field')

    # magazine issue info
    magazine_issue_info_parser = magazine_issue_subparsers.add_parser('info', help='show information of a magazine issue')
    magazine_issue_info_parser.add_argument('issue', help='issue')

    # magazine issue list
    magazine_issue_list_parser = magazine_issue_subparsers.add_parser('list', help='list issues of a magazine')
    magazine_issue_list_parser.add_argument('-shelf', choices=['read', 'unread'], help='filter on shelves')
    magazine_issue_list_parser.add_argument('-s', '--search', help='filter on shelves')

    # magazine issue reads
    magazine_issue_read_parser = magazine_issue_subparsers.add_parser('read', help='manage read of papers')
    magazine_issue_read_parser.add_argument('issue', help='of which issue to manage a read')
    magazine_issue_read_subparser = magazine_issue_read_parser.add_subparsers(dest='paper_read_subparsers')

    magazine_issue_read_add_parser = magazine_issue_read_subparser.add_parser('add', help='manage addition of reads')
    magazine_issue_read_add_parser.add_argument('-started', default=None, type=valid_date, help='date started')
    magazine_issue_read_add_parser.add_argument('-finished', default=None, type=valid_date, help='date finished')

    magazine_issue_read_edit_parser = magazine_issue_read_subparser.add_parser('edit', help='manage edition of reads')
    magazine_issue_read_edit_parser.add_argument('id', type=int, help='which read to edit')
    magazine_issue_read_edit_parser.add_argument('field', choices=['started', 'finished'], help='which field to edit')
    magazine_issue_read_edit_parser.add_argument('value', type=valid_date, help='new value for field')

    magazine_issue_read_delete_parser = magazine_issue_read_subparser.add_parser('delete', help='manage deletion of reads')
    magazine_issue_read_delete_parser.add_argument('id', type=int, help='which read to delete')

    # magazine list
    magazine_list_parser = magazine_subparsers.add_parser('list', help='list magazines')
    magazine_list_parser.add_argument('-s', '--search', help='filter on shelves')


    # create the parser for the "paper" subcommand
    paper_parser = subparsers.add_parser('paper', help='subcommand for papers')
    paper_parser.set_defaults(func=_paper)
    paper_subparsers = paper_parser.add_subparsers(dest='paper_subparsers')

    # paper acquisitions
    paper_acquisition_parser = paper_subparsers.add_parser('acquisition', help='manage acquisition of papers')
    paper_acquisition_parser.add_argument('paper', help='of which paper to manage an acquisition')
    paper_acquisition_subparser = paper_acquisition_parser.add_subparsers(dest='paper_acquisition_subparsers')

    paper_acquisition_add_parser = paper_acquisition_subparser.add_parser('add', help='manage addition of acquisitions')
    paper_acquisition_add_parser.add_argument('-date', default=None, type=valid_date, help='date')
    paper_acquisition_add_parser.add_argument('-price', default=0, type=float, help='price')

    paper_acquisition_edit_parser = paper_acquisition_subparser.add_parser('edit', help='manage edition of acquisitions')
    paper_acquisition_edit_parser.add_argument('id', type=int, help='which acquisition to edit')

    paper_acquisition_edit_subparser = paper_acquisition_edit_parser.add_subparsers(dest='paper_acquisition_edit_subparsers', help='which field to edit')
    paper_acquisition_edit_date_parser = paper_acquisition_edit_subparser.add_parser('date')
    paper_acquisition_edit_date_parser.add_argument('value', type=valid_date, help='new value for field')

    paper_acquisition_edit_price_parser = paper_acquisition_edit_subparser.add_parser('price')
    paper_acquisition_edit_price_parser.add_argument('value', type=float, help='new value for field')

    paper_acquisition_delete_parser = paper_acquisition_subparser.add_parser('delete', help='manage deletion of acquisitions')
    paper_acquisition_delete_parser.add_argument('id', type=int, help='which acquisition to delete')

    # paper add
    paper_add_parser = paper_subparsers.add_parser('add', help='add a paper')
    paper_add_parser.add_argument('title', help='title of the paper')
    paper_add_parser.add_argument('--published_on', type=valid_date, help='published on date of the paper')
    paper_add_parser.add_argument('--journal', type=int, help='journal of the paper')
    paper_add_parser.add_argument('--volume', help='volume of the paper')

    # paper edit
    paper_edit_parser = paper_subparsers.add_parser('edit', help='edit paper')
    paper_edit_parser.add_argument('paper', help='which paper to edit')
    paper_edit_subparser = paper_edit_parser.add_subparsers(dest='paper_edit_subparsers')

    paper_edit_title_parser = paper_edit_subparser.add_parser('title', help='edit title field')
    paper_edit_title_parser.add_argument('value', help='new value for title field')

    paper_edit_published_on_parser = paper_edit_subparser.add_parser('published_on', help='edit published_on field')
    paper_edit_published_on_parser.add_argument('value', type=valid_date, help='new value for published_on field')

    paper_edit_journal_parser = paper_edit_subparser.add_parser('journal', help='edit journal field')
    paper_edit_journal_parser.add_argument('value', type=int, help='new value for journal field')

    paper_edit_volume_parser = paper_edit_subparser.add_parser('volume', help='edit volume field')
    paper_edit_volume_parser.add_argument('value', help='new value for volume field')

    # paper list
    paper_list_parser = paper_subparsers.add_parser('list', help='list papers')
    paper_list_parser.add_argument('shelf', choices=['read', 'unread'], nargs='?', help='filter on shelves')
    paper_list_parser.add_argument('-s', '--search', nargs='?', help='search for papers')

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
    paper_read_parser.add_argument('paper', help='which paper to edit')
    paper_read_subparser = paper_read_parser.add_subparsers(dest='paper_read_subparsers')

    paper_read_add_parser = paper_read_subparser.add_parser('add', help='manage addition of reads')
    paper_read_add_parser.add_argument('-started', default=None, type=valid_date, help='date started')
    paper_read_add_parser.add_argument('-finished', default=None, type=valid_date, help='date finished')

    paper_read_delete_parser = paper_read_subparser.add_parser('delete', help='manage deletion of reads')
    paper_read_delete_parser.add_argument('id', type=int, help='which read to delete')

    paper_read_edit_parser = paper_read_subparser.add_parser('edit', help='manage edition of reads')
    paper_read_edit_parser.add_argument('id', type=int, help='which read to edit')
    paper_read_edit_parser.add_argument('field', choices=['started', 'finished'], help='which field to edit')
    paper_read_edit_parser.add_argument('value', type=valid_date, help='new value for field')


    # create the parser for the "person" subcommand
    person_parser = subparsers.add_parser('person', help='manage persons')
    person_parser.set_defaults(func=_person)
    person_subparsers = person_parser.add_subparsers(dest='person_subparsers')

    # person add
    person_add_parser = person_subparsers.add_parser('add', help='add a person')
    person_add_parser.add_argument('first_name', help='first name')
    person_add_parser.add_argument('last_name', help='last name')

    # person edit
    person_edit_parser = person_subparsers.add_parser('edit', help='edit a person')
    person_edit_parser.add_argument('person', help='which person to edit')
    person_edit_parser.add_argument('field', choices=['first_name', 'last_name'], help='field to edit')
    person_edit_parser.add_argument('value', help='new value for field')

    # person info
    person_info_parser = person_subparsers.add_parser('info', help='show information of a person')
    person_info_parser.add_argument('person', help='which person to show information of')

    # person list
    person_list_parser = person_subparsers.add_parser('list', help='list persons')
    person_list_parser.add_argument('-s', '--search', help='search by term')


    # create the parser for the "publisher" subcommand
    publisher_parser = subparsers.add_parser('publisher', help='manage publishers')
    publisher_parser.set_defaults(func=_publisher)
    publisher_subparsers = publisher_parser.add_subparsers(dest='publisher_subparsers')

    # publisher add
    publisher_add_parser = publisher_subparsers.add_parser('add', help='add a publisher')
    publisher_add_parser.add_argument('name', help='name')
    publisher_add_parser.add_argument('-l', '--link', nargs='*', default=[], help='links')

    # publisher edit
    publisher_edit_parser = publisher_subparsers.add_parser('edit', help='edit a publisher')
    publisher_edit_parser.add_argument('publisher', help='which publisher to edit')
    publisher_edit_parser.add_argument('field', choices=['name'], help='field to edit')
    publisher_edit_parser.add_argument('value', help='new value for field')

    # publisher info
    publisher_info_parser = publisher_subparsers.add_parser('info', help='show information of a publisher')
    publisher_info_parser.add_argument('publisher', help='which publisher to show information of')

    # publisher list
    publisher_list_parser = publisher_subparsers.add_parser('list', help='list publishers')
    publisher_list_parser.add_argument('-s', '--search', help='search by term')


    # create the parser for the "series" subcommand
    series_parser = subparsers.add_parser('series', help='manage series')
    series_parser.set_defaults(func=_series)
    series_subparsers = series_parser.add_subparsers(dest='series_subparsers')

    # series add
    series_add_parser = series_subparsers.add_parser('add', help='add a series')
    series_add_parser.add_argument('name', help='name')

    # series edit
    series_edit_parser = series_subparsers.add_parser('edit', help='edit a series')
    series_edit_parser.add_argument('series', help='which series to edit')
    series_edit_parser.add_argument('field', choices=['name'], help='field to edit')
    series_edit_parser.add_argument('value', help='new value for field')

    # series info
    series_info_parser = series_subparsers.add_parser('info', help='show information of series')
    series_info_parser.add_argument('name', help='series name')

    # series list
    series_info_parser = series_subparsers.add_parser('info', help='show information of a series')
    series_info_parser.add_argument('series', help='which series to show information of')


    # create the parser for the "runserver" subcommand
    runserver_parser = subparsers.add_parser('runserver', help='subcommand for local http server')
    runserver_parser.set_defaults(func=_runserver)


    args = parser.parse_args()
    if args.subparser:
        args.func(args)
    else:
        parser.print_usage()

    # from bibliothek.functions.parsers.freies_magazin import FreiesMagazinRSSParser
    # parser = FreiesMagazinRSSParser()
    # parser.archive()
