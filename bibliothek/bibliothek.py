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


def _binding(args):
    import bindings.functions
    if args.binding_subparser == 'add':
        bindings.functions.binding.create(args.name)
    elif args.binding_subparser == 'edit':
        binding = bindings.functions.binding.get.by_term(args.binding)
        if binding:
            bindings.functions.binding.edit(binding, args.field, args.value)
    elif args.binding_subparser == 'info':
        binding = bindings.functions.binding.get.by_term(args.binding)
        if binding:
            bindings.functions.binding.info(binding)
    elif args.binding_subparser == 'list':
        if args.search:
            bindings.functions.binding.list.by_term(args.search)
        else:
            bindings.functions.binding.list.all()
    else:
        binding_parser.print_help()


def _book(args):
    import books.functions
    if args.book_subparser == 'add':
        books.functions.book.create(args.title, args.author, args.series, args.volume, args.genre, args.link)
    elif args.book_subparser == 'edit':
        book = books.functions.book.get.by_term(args.book)
        if book:
            books.functions.book.edit(book, args.book_edit_subparser, args.value)
    elif args.book_subparser == 'edition':
        book = books.functions.book.get.by_term(args.book)
        if args.book_edition_subparser == 'acquisition' and book:
            edition = books.functions.edition.get.by_term(book, args.edition)
            if args.book_edition_acquisition_subparser == 'add' and edition:
                books.functions.edition.acquisition.add(edition, args.date, args.price)
            elif args.book_edition_acquisition_subparser == 'delete' and edition:
                books.functions.edition.acquisition.delete(edition, args.acquisition)
            elif args.book_edition_acquisition_subparser == 'edit' and edition:
                books.functions.edition.acquisition.edit(edition, args.acquisition, args.book_edition_acquisition_edit_subparser, args.value)
        elif args.book_edition_subparser == 'add' and book:
            books.functions.edition.create(book, args.isbn, args.published_on, args.cover, args.binding, args.publisher, args.language, args.file)
        elif args.book_edition_subparser == 'edit' and book:
            edition = books.functions.edition.get.by_term(book, args.edition)
            if edition:
                books.functions.edition.edit(edition, args.book_edition_edit_subparser, args.value)
        elif args.book_edition_subparser == 'info' and book:
            edition = books.functions.edition.get.by_term(book, args.edition)
            if edition:
                books.functions.edition.info(edition)
        elif args.book_edition_subparser == 'list' and book:
            if args.search:
                books.functions.edition.list.by_term(book, args.search)
            else:
                books.functions.edition.list.all(book)
        elif args.book_edition_subparser == 'read' and book:
            edition = books.functions.edition.get.by_term(book, args.edition)
            if args.book_edition_read_subparsers == 'add' and edition:
                books.functions.edition.read.add(edition, args.started, args.finished)
            elif args.book_edition_read_subparsers == 'delete' and edition:
                books.functions.edition.read.delete(edition, args.read)
            elif args.book_edition_read_subparsers == 'edit' and edition:
                books.functions.edition.read.edit(edition, args.read, args.field, args.value)
        else:
            book_edition_parser.print_help()
    elif args.book_subparser == 'info':
        book = books.functions.book.get.by_term(args.book)
        if book:
            books.functions.book.info(book)
    elif args.book_subparser == 'list':
        if args.shelf:
            books.functions.book.list.by_shelf(args.shelf)
        elif args.search:
            books.functions.book.list.by_term(args.search)
        else:
            books.functions.book.list.all()
    else:
        book_parser.print_help()


def _genre(args):
    import genres.functions
    if args.genre_subparser == 'add':
        genres.functions.genre.create(args.name)
    elif args.genre_subparser == 'edit':
        genre = genres.functions.genre.get.by_term(args.genre)
        if genre:
            genres.functions.genre.edit(genre, args.field, args.value)
    elif args.genre_subparser == 'info':
        genre = genres.functions.genre.get.by_term(args.genre)
        if genre:
            genres.functions.genre.info(genre)
    elif args.genre_subparser == 'list':
        if args.search:
            genres.functions.genre.list.by_term(args.search)
        else:
            genres.functions.genre.list.all()
    else:
        genre_parser.print_help()


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
                magazines.functions.issue.acquisition.add(issue, args.date, args.price)
            elif args.magazine_issue_acquisition_subparser == 'delete' and issue:
                magazines.functions.issue.acquisition.delete(issue, args.acquisition)
            elif args.magazine_issue_acquisition_subparser == 'edit' and issue:
                magazines.functions.issue.acquisition.edit(issue, args.acquisition, args.magazine_issue_acquisition_edit_subparser, args.value)
        elif args.magazine_issue_subparser == 'add' and magazine:
            magazines.functions.issue.create(magazine, args.issue, args.published_on, args.cover, args.link, args.file)
        elif args.magazine_issue_subparser == 'edit' and magazine:
            issue = magazines.functions.issue.get.by_term(magazine, args.issue)
            if issue:
                magazines.functions.issue.edit(issue, args.field, args.value)
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
                magazines.functions.issue.read.add(issue, args.started, args.finished)
            elif args.magazine_issue_read_subparsers == 'delete' and issue:
                magazines.functions.issue.read.delete(issue, args.read)
            elif args.magazine_issue_read_subparsers == 'edit' and issue:
                magazines.functions.issue.read.edit(issue, args.read, args.field, args.value)
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
            papers.functions.paper.acquisition.add(paper, args.date, args.price)
        elif args.paper_acquisition_subparser == 'delete' and paper:
            papers.functions.paper.acquisition.delete(paper, args.acquisition)
        elif args.paper_acquisition_subparser == 'edit' and paper:
            papers.functions.paper.acquisition.edit(paper, args.acquisition, args.paper_acquisition_edit_subparser, args.value)
    elif args.paper_subparser == 'add':
        papers.functions.paper.create(args.title, args.author, args.published_on, args.journal, args.volume, args.language, args.link)
    elif args.paper_subparser == 'edit':
        paper = papers.functions.paper.get.by_term(args.paper)
        if paper:
            papers.functions.paper.edit(paper, args.paper_edit_subparser, args.value)
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
            papers.functions.paper.read.add(paper, args.started, args.finished)
        elif args.paper_read_subparsers == 'delete' and paper:
            papers.functions.paper.read.delete(paper, args.read)
        elif args.paper_read_subparsers == 'edit' and paper:
            papers.functions.paper.read.edit(paper, args.read, args.field, args.value)
    else:
        paper_parser.print_help()


def _person(args):
    import persons.functions
    if args.person_subparser == 'add':
        persons.functions.person.create(args.first_name, args.last_name, args.link)
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
            publishers.functions.publisher.edit(publisher, args.field, args.value)
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
        series.functions.series.create(args.name)
    elif args.series_subparser == 'edit':
        series_obj = series.functions.series.get.by_term(args.series)
        if series_obj:
            series.functions.series.edit(series_obj, args.field, args.value)
    elif args.series_subparser == 'info':
        series_obj = series.functions.series.get.by_term(args.series)
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
    execute_from_command_line(sys.argv + ['--insecure'])


if __name__ == "__main__":
    init()


    parser = ArgumentParser(prog=settings.APP_NAME, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version=settings.APP_VERSION)
    subparsers = parser.add_subparsers(dest='subparser')


    # create the parser for the "binding" subcommand
    binding_parser = subparsers.add_parser('binding', help='manage bindings')
    binding_parser.set_defaults(func=_binding)
    binding_subparser = binding_parser.add_subparsers(dest='binding_subparser')

    # binding add
    binding_add_parser = binding_subparser.add_parser('add', help='add a binding')
    binding_add_parser.add_argument('name', help='name')

    # binding edit
    binding_edit_parser = binding_subparser.add_parser('edit', help='edit a binding')
    binding_edit_parser.add_argument('binding', help='which binding to edit')
    binding_edit_parser.add_argument('field', choices=['name'], help='which field to edit')
    binding_edit_parser.add_argument('value', help='new value for field')

    # binding info
    binding_info_parser = binding_subparser.add_parser('info', help='show information of a binding')
    binding_info_parser.add_argument('binding', help='of which binding to show information')

    # binding list
    binding_list_parser = binding_subparser.add_parser('list', help='list bindings')
    binding_list_parser.add_argument('-s', '--search', help='filter by term')


    # create the parser for the "book" subcommand
    book_parser = subparsers.add_parser('book', help='manage books')
    book_parser.set_defaults(func=_book)
    book_subparser = book_parser.add_subparsers(dest='book_subparser')

    # book add
    book_add_parser = book_subparser.add_parser('add', help='add a book')
    book_add_parser.add_argument('title', help='title')
    book_add_parser.add_argument('-a', '--author', nargs='*', default=[], help='authors')
    book_add_parser.add_argument('-s', '--series', default=None, help='series')
    book_add_parser.add_argument('-v', '--volume', default=None, type=float, help='series volume')
    book_add_parser.add_argument('-g', '--genre', nargs='*', default=[], help='genres')
    book_add_parser.add_argument('-l', '--link', nargs='*', default=[], help='links')

    # book edit
    book_edit_parser = book_subparser.add_parser('edit', help='edit a book', prefix_chars='_')
    book_edit_parser.add_argument('book', help='which book to edit')
    book_edit_subparser = book_edit_parser.add_subparsers(dest='book_edit_subparser', help='which field to edit')

    book_edit_title_parser = book_edit_subparser.add_parser('title')
    book_edit_title_parser.add_argument('value', help='new value for field')

    book_edit_add_author_parser = book_edit_subparser.add_parser('+author')
    book_edit_add_author_parser.add_argument('value', help='new value for field')

    book_edit_remove_author_parser = book_edit_subparser.add_parser('-author')
    book_edit_remove_author_parser.add_argument('value', help='new value for field')

    book_edit_series_parser = book_edit_subparser.add_parser('series')
    book_edit_series_parser.add_argument('value', help='new value for field')

    book_edit_volume_parser = book_edit_subparser.add_parser('volume')
    book_edit_volume_parser.add_argument('value', type=float, help='new value for field')

    book_edit_add_genre_parser = book_edit_subparser.add_parser('+genre')
    book_edit_add_genre_parser.add_argument('value', help='new value for field')

    book_edit_remove_genre_parser = book_edit_subparser.add_parser('-genre')
    book_edit_remove_genre_parser.add_argument('value', help='new value for field')

    # book edition
    book_edition_parser = book_subparser.add_parser('edition', help='manage editions of a book')
    book_edition_parser.add_argument('book', help='editions of which book')
    book_edition_subparser = book_edition_parser.add_subparsers(dest='book_edition_subparser')

    # book edition acquisitions
    book_edition_acquisition_parser = book_edition_subparser.add_parser('acquisition', help='manage acquisition of a book edition')
    book_edition_acquisition_parser.add_argument('edition', help='of which edition to manage an acquisition')
    book_edition_acquisition_subparser = book_edition_acquisition_parser.add_subparsers(dest='book_edition_acquisition_subparser')

    book_edition_acquisition_add_parser = book_edition_acquisition_subparser.add_parser('add', help='add an acquisition')
    book_edition_acquisition_add_parser.add_argument('--date', default=None, type=valid_date, help='date')
    book_edition_acquisition_add_parser.add_argument('--price', default=0, type=float, help='price')

    book_edition_acquisition_delete_parser = book_edition_acquisition_subparser.add_parser('delete', help='delete an acquisition')
    book_edition_acquisition_delete_parser.add_argument('acquisition', type=int, help='which acquisition to delete')

    book_edition_acquisition_edit_parser = book_edition_acquisition_subparser.add_parser('edit', help='edit an acquisition')
    book_edition_acquisition_edit_parser.add_argument('acquisition', type=int, help='which acquisition to edit')

    book_edition_acquisition_edit_subparser = book_edition_acquisition_edit_parser.add_subparsers(dest='book_edition_acquisition_edit_subparser', help='which field to edit')
    book_edition_acquisition_edit_date_parser = book_edition_acquisition_edit_subparser.add_parser('date')
    book_edition_acquisition_edit_date_parser.add_argument('value', type=valid_date, help='new value for field')

    book_edition_acquisition_edit_price_parser = book_edition_acquisition_edit_subparser.add_parser('price')
    book_edition_acquisition_edit_price_parser.add_argument('value', type=float, help='new value for field')

    # book edition add
    book_edition_add_parser = book_edition_subparser.add_parser('add', help='add an edition to a book')
    book_edition_add_parser.add_argument('-i', '--isbn', help='ISBN')
    book_edition_add_parser.add_argument('-p', '--published_on', type=valid_date, help='published on')
    book_edition_add_parser.add_argument('-c', '--cover', help='path to a cover image')
    book_edition_add_parser.add_argument('-b', '--binding', help='binding')
    book_edition_add_parser.add_argument('-u', '--publisher', help='publisher')
    book_edition_add_parser.add_argument('-f', '--file', nargs='*', default=[], help='files')
    book_edition_add_parser.add_argument('-l', '--language', nargs='*', default=[], help='languages')

    # book edition edit
    book_edition_edit_parser = book_edition_subparser.add_parser('edit', help='edit a book edition', prefix_chars='_')
    book_edition_edit_parser.add_argument('edition', help='which edition to edit')
    book_edition_edit_subparser = book_edition_edit_parser.add_subparsers(dest='book_edition_edit_subparser', help='which field to edit')

    book_edition_edit_edition_parser = book_edition_edit_subparser.add_parser('isbn')
    book_edition_edit_edition_parser.add_argument('value', help='new value for field')

    book_edition_edit_published_on_parser = book_edition_edit_subparser.add_parser('published_on')
    book_edition_edit_published_on_parser.add_argument('value', type=valid_date, help='new value for field')

    book_edition_edit_cover_parser = book_edition_edit_subparser.add_parser('cover')
    book_edition_edit_cover_parser.add_argument('value', help='new value for field')

    book_edition_edit_binding_parser = book_edition_edit_subparser.add_parser('binding')
    book_edition_edit_binding_parser.add_argument('value', help='new value for field')

    book_edition_edit_publisher_parser = book_edition_edit_subparser.add_parser('publisher')
    book_edition_edit_publisher_parser.add_argument('value', help='new value for field')

    book_edition_edit_add_language_parser = book_edition_edit_subparser.add_parser('+language')
    book_edition_edit_add_language_parser.add_argument('value', help='new value for field')

    book_edition_edit_remove_language_parser = book_edition_edit_subparser.add_parser('-language')
    book_edition_edit_remove_language_parser.add_argument('value', help='new value for field')

    book_edition_edit_add_file_parser = book_edition_edit_subparser.add_parser('+file')
    book_edition_edit_add_file_parser.add_argument('value', help='new value for field')

    # book edition info
    book_edition_info_parser = book_edition_subparser.add_parser('info', help='show information of a book edition')
    book_edition_info_parser.add_argument('edition', help='of which edition to show information')

    # book edition list
    book_edition_list_parser = book_edition_subparser.add_parser('list', help='list editions of a book')
    book_edition_list_parser.add_argument('--shelf', choices=['read', 'unread'], help='filter on shelves')
    book_edition_list_parser.add_argument('-s', '--search', help='search by term')

    # book edition reads
    book_edition_read_parser = book_edition_subparser.add_parser('read', help='manage read of papers')
    book_edition_read_parser.add_argument('edition', help='of which edition to manage a read')
    book_edition_read_subparsers = book_edition_read_parser.add_subparsers(dest='book_edition_read_subparsers')

    book_edition_read_add_parser = book_edition_read_subparsers.add_parser('add', help='add a read')
    book_edition_read_add_parser.add_argument('--started', default=None, type=valid_date, help='date started')
    book_edition_read_add_parser.add_argument('--finished', default=None, type=valid_date, help='date finished')

    book_edition_read_delete_parser = book_edition_read_subparsers.add_parser('delete', help='delete a read')
    book_edition_read_delete_parser.add_argument('read', type=int, help='which read to delete')

    book_edition_read_edit_parser = book_edition_read_subparsers.add_parser('edit', help='edit a read')
    book_edition_read_edit_parser.add_argument('read', type=int, help='which read to edit')
    book_edition_read_edit_parser.add_argument('field', choices=['started', 'finished'], help='which field to edit')
    book_edition_read_edit_parser.add_argument('value', type=valid_date, help='new value for field')

    # book info
    book_info_parser = book_subparser.add_parser('info', help='show information of a book')
    book_info_parser.add_argument('book', help='of which book to show information')

    # book list
    book_list_parser = book_subparser.add_parser('list', help='list books')
    book_list_parser.add_argument('--shelf', choices=['read', 'unread'], help='filter on shelves')
    book_list_parser.add_argument('-s', '--search', help='search by term')


    # create the parser for the "genre" subcommand
    genre_parser = subparsers.add_parser('genre', help='manage genres')
    genre_parser.set_defaults(func=_genre)
    genre_subparser = genre_parser.add_subparsers(dest='genre_subparser')

    # genre add
    genre_add_parser = genre_subparser.add_parser('add', help='add a genre')
    genre_add_parser.add_argument('name', help='name')

    # genre edit
    genre_edit_parser = genre_subparser.add_parser('edit', help='edit a genre')
    genre_edit_parser.add_argument('genre', help='which genre to edit')
    genre_edit_parser.add_argument('field', choices=['name'], help='which field to edit')
    genre_edit_parser.add_argument('value', help='new value for field')

    # genre info
    genre_info_parser = genre_subparser.add_parser('info', help='show information of a genre')
    genre_info_parser.add_argument('genre', help='of which genre to show information')

    # genre list
    genre_list_parser = genre_subparser.add_parser('list', help='list genres')
    genre_list_parser.add_argument('-s', '--search', help='filter by term')


    # create the parser for the "journal" subcommand
    journal_parser = subparsers.add_parser('journal', help='manage journals')
    journal_parser.set_defaults(func=_journal)
    journal_subparser = journal_parser.add_subparsers(dest='journal_subparser')

    # journal add
    journal_add_parser = journal_subparser.add_parser('add', help='add a journal')
    journal_add_parser.add_argument('name', help='name')
    journal_add_parser.add_argument('-l', '--link', nargs='*', default=[], help='links')

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
    journal_list_parser.add_argument('-s', '--search', help='filter by term')


    # create the parser for the "magazine" subcommand
    magazine_parser = subparsers.add_parser('magazine', help='manage magazines')
    magazine_parser.set_defaults(func=_magazine)
    magazine_subparser = magazine_parser.add_subparsers(dest='magazine_subparser')

    # magazine add
    magazine_add_parser = magazine_subparser.add_parser('add', help='add a magazine')
    magazine_add_parser.add_argument('name', help='name')
    magazine_add_parser.add_argument('-f', '--feed', help='feed url')
    magazine_add_parser.add_argument('-l', '--link', nargs='*', default=[], help='links')

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
    magazine_issue_add_parser.add_argument('-p', '--published_on', type=valid_date, help='published on')
    magazine_issue_add_parser.add_argument('-c', '--cover', help='path to a cover image')
    magazine_issue_add_parser.add_argument('-l', '--link', nargs='*', default=[], help='links')
    magazine_issue_add_parser.add_argument('-f', '--file', nargs='*', default=[], help='files')

    # magazine issue edit
    magazine_issue_edit_parser = magazine_issue_subparser.add_parser('edit', help='edit a magazine issue')
    magazine_issue_edit_parser.add_argument('issue', help='which issue to edit')

    magazine_issue_edit_subparser = magazine_issue_edit_parser.add_subparsers(dest='magazine_issue_edit_subparser', help='which field to edit')
    magazine_issue_edit_issue_parser = magazine_issue_edit_subparser.add_parser('issue')
    magazine_issue_edit_issue_parser.add_argument('value', help='new value for field')

    magazine_issue_edit_published_on_parser = magazine_issue_edit_subparser.add_parser('published_on')
    magazine_issue_edit_published_on_parser.add_argument('value', type=valid_date, help='new value for field')

    magazine_issue_edit_cover_parser = magazine_issue_edit_subparser.add_parser('cover')
    magazine_issue_edit_cover_parser.add_argument('value', help='new value for field')

    # magazine issue info
    magazine_issue_info_parser = magazine_issue_subparser.add_parser('info', help='show information of a magazine issue')
    magazine_issue_info_parser.add_argument('issue', help='of which issue to show information')

    # magazine issue list
    magazine_issue_list_parser = magazine_issue_subparser.add_parser('list', help='list issues of a magazine')
    magazine_issue_list_parser.add_argument('--shelf', choices=['read', 'unread'], help='filter on shelves')
    magazine_issue_list_parser.add_argument('-s', '--search', help='search by term')

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
    magazine_list_parser.add_argument('-s', '--search', help='search by term')


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
    paper_add_parser.add_argument('-a', '--author', nargs='*', default=[], help='authors')
    paper_add_parser.add_argument('-p', '--published_on', type=valid_date, help='published on')
    paper_add_parser.add_argument('-j', '--journal', help='journal')
    paper_add_parser.add_argument('-v', '--volume', help='journal volume')
    paper_add_parser.add_argument('-n', '--language', nargs='*', default=[], help='languages')
    paper_add_parser.add_argument('-l', '--link', nargs='*', default=[], help='links')

    # paper edit
    paper_edit_parser = paper_subparser.add_parser('edit', help='edit a paper', prefix_chars='_')
    paper_edit_parser.add_argument('paper', help='which paper to edit')
    paper_edit_subparser = paper_edit_parser.add_subparsers(dest='paper_edit_subparser', help='which field to edit')

    paper_edit_title_parser = paper_edit_subparser.add_parser('title')
    paper_edit_title_parser.add_argument('value', help='new value for field')

    paper_edit_published_on_parser = paper_edit_subparser.add_parser('published_on')
    paper_edit_published_on_parser.add_argument('value', type=valid_date, help='new value for field')

    paper_edit_journal_parser = paper_edit_subparser.add_parser('journal')
    paper_edit_journal_parser.add_argument('value', help='new value for field')

    paper_edit_volume_parser = paper_edit_subparser.add_parser('volume')
    paper_edit_volume_parser.add_argument('value', help='new value for field')

    paper_edit_add_language_parser = paper_edit_subparser.add_parser('+language')
    paper_edit_add_language_parser.add_argument('value', help='new value for field')

    paper_edit_remove_language_parser = paper_edit_subparser.add_parser('-language')
    paper_edit_remove_language_parser.add_argument('value', help='new value for field')

    paper_edit_add_file_parser = paper_edit_subparser.add_parser('+file')
    paper_edit_add_file_parser.add_argument('value', help='new value for field')

    # paper list
    paper_list_parser = paper_subparser.add_parser('list', help='list papers')
    paper_list_parser.add_argument('--shelf', choices=['read', 'unread'], nargs='?', help='filter on shelves')
    paper_list_parser.add_argument('-s', '--search', help='search by term')

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
    person_add_parser.add_argument('-l', '--link', nargs='*', default=[], help='links')

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
    person_list_parser.add_argument('-s', '--search', help='search by term')


    # create the parser for the "publisher" subcommand
    publisher_parser = subparsers.add_parser('publisher', help='manage publishers')
    publisher_parser.set_defaults(func=_publisher)
    publisher_subparser = publisher_parser.add_subparsers(dest='publisher_subparser')

    # publisher add
    publisher_add_parser = publisher_subparser.add_parser('add', help='add a publisher')
    publisher_add_parser.add_argument('name', help='name')
    publisher_add_parser.add_argument('-l', '--link', nargs='*', default=[], help='links')

    # publisher edit
    publisher_edit_parser = publisher_subparser.add_parser('edit', help='edit a publisher')
    publisher_edit_parser.add_argument('publisher', help='which publisher to edit')
    publisher_edit_parser.add_argument('field', choices=['name'], help='field to edit')
    publisher_edit_parser.add_argument('value', help='new value for field')

    # publisher info
    publisher_info_parser = publisher_subparser.add_parser('info', help='show information of a publisher')
    publisher_info_parser.add_argument('publisher', help='of which publisher to show information')

    # publisher list
    publisher_list_parser = publisher_subparser.add_parser('list', help='list publishers')
    publisher_list_parser.add_argument('-s', '--search', help='search by term')


    # create the parser for the "series" subcommand
    series_parser = subparsers.add_parser('series', help='manage series')
    series_parser.set_defaults(func=_series)
    series_subparser = series_parser.add_subparsers(dest='series_subparser')

    # series add
    series_add_parser = series_subparser.add_parser('add', help='add a series')
    series_add_parser.add_argument('name', help='name')

    # series edit
    series_edit_parser = series_subparser.add_parser('edit', help='edit a series')
    series_edit_parser.add_argument('series', help='which series to edit')
    series_edit_parser.add_argument('field', choices=['name'], help='field to edit')
    series_edit_parser.add_argument('value', help='new value for field')

    # series info
    series_info_parser = series_subparser.add_parser('info', help='show information of series')
    series_info_parser.add_argument('name', help='series name')

    # series list
    series_list_parser = series_subparser.add_parser('list', help='list seriess')
    series_list_parser.add_argument('-s', '--search', help='search by term')


    # create the parser for the "runserver" subcommand
    runserver_parser = subparsers.add_parser('runserver', help='start local http server')
    runserver_parser.set_defaults(func=_runserver)


    args = parser.parse_args()
    if args.subparser:
        args.func(args)
    else:
        parser.print_usage()

    # from bibliothek.functions.parsers.freies_magazin import FreiesMagazinRSSParser
    # parser = FreiesMagazinRSSParser()
    # parser.archive()
