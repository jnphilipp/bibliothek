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

import os
import sys

from bibliothek.argparse import valid_date
from books.functions import book as fbook, edition as fedition
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from shelves.argparse import acquisition_subparser, read_subparser


def _book(args):
    if args.subparser == 'add':
        fbook.create(args.title, args.author, args.series, args.volume,
                     args.genre, args.link)
    elif args.subparser == 'edit':
        book = fbook.get.by_term(args.book)
        if book:
            fbook.edit(book, args.edit_subparser, args.value)
    elif args.subparser == 'edition':
        book = fbook.get.by_term(args.book)
        if args.edition_subparser == 'acquisition' and book:
            edition = fedition.get.by_term(book, args.edition)
            if args.acquisition_subparser == 'add' and edition:
                fedition.acquisition.add(edition, args.date, args.price)
            elif args.acquisition_subparser == 'delete' and edition:
                fedition.acquisition.delete(edition, args.acquisition)
            elif args.acquisition_subparser == 'edit' and edition:
                fedition.acquisition.edit(edition, args.acquisition,
                                          args.edit_subparser, args.value)
        elif args.edition_subparser == 'add' and book:
            fedition.create(book, args.alternate_title, args.isbn,
                            args.publishing_date, args.cover, args.binding,
                            args.publisher, args.language, args.file)
        elif args.edition_subparser == 'edit' and book:
            edition = fedition.get.by_term(book, args.edition)
            if edition:
                fedition.edit(edition, args.edit_subparser, args.value)
        elif args.edition_subparser == 'info' and book:
            edition = fedition.get.by_term(book, args.edition)
            if edition:
                fedition.info(edition)
        elif args.edition_subparser == 'list' and book:
            if args.search:
                fedition.list.by_term(book, args.search)
            else:
                fedition.list.all(book)
        elif args.edition_subparser == 'open' and book:
            edition = fedition.get.by_term(book, args.edition)
            if edition:
                file = edition.files.get(pk=args.file)
                path = os.path.join(settings.MEDIA_ROOT, file.file.path)
                if sys.platform == 'linux':
                    os.system('xdg-open "%s"' % path)
                else:
                    os.system('open "%s"' % path)
        elif args.edition_subparser == 'read' and book:
            edition = fedition.get.by_term(book, args.edition)
            if args.read_subparser == 'add' and edition:
                fedition.read.add(edition, args.started, args.finished)
            elif args.read_subparser == 'delete' and edition:
                fedition.read.delete(edition, args.read)
            elif args.read_subparser == 'edit' and edition:
                fedition.read.edit(edition, args.read, args.field, args.value)
    elif args.subparser == 'info':
        book = fbook.get.by_term(args.book)
        if book:
            fbook.info(book)
    elif args.subparser == 'list':
        if args.shelf:
            fbook.list.by_shelf(args.shelf)
        elif args.search:
            fbook.list.by_term(args.search)
        else:
            fbook.list.all()


def add_subparser(parser):
    book_parser = parser.add_parser('book', help=_('Manage books'))
    book_parser.set_defaults(func=_book)
    subparser = book_parser.add_subparsers(dest='subparser')
    edition_subparser(subparser)

    # book add
    add_parser = subparser.add_parser('add', help=_('Add a book'))
    add_parser.add_argument('title', help=_('Title'))
    add_parser.add_argument('--author', nargs='*', default=[],
                            help=_('Authors'))
    add_parser.add_argument('--series', default=None, help=_('Series'))
    add_parser.add_argument('--volume', default=None, type=float,
                            help=_('Series volume'))
    add_parser.add_argument('--genre', nargs='*', default=[], help=_('Genres'))
    add_parser.add_argument('--link', nargs='*', default=[], help=_('Links'))

    # book edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a book'))
    edit_parser.add_argument('book', help='which book to edit')
    edit_subparser = edit_parser.add_subparsers(dest='edit_subparser',
                                                help=_('Which field to edit'))

    edit_title_parser = edit_subparser.add_parser('title')
    edit_title_parser.add_argument('value', help=_('New value for field'))

    edit_author_parser = edit_subparser.add_parser('author')
    edit_author_parser.add_argument('value', help=_('New value for field'))

    edit_series_parser = edit_subparser.add_parser('series')
    edit_series_parser.add_argument('value', help=_('New value for field'))

    edit_volume_parser = edit_subparser.add_parser('volume')
    edit_volume_parser.add_argument('value', type=float,
                                    help=_('New value for field'))

    edit_genre_parser = edit_subparser.add_parser('genre')
    edit_genre_parser.add_argument('value', help=_('New value for field'))

    edit_link_parser = edit_subparser.add_parser('link')
    edit_link_parser.add_argument('value', help=_('New value for field'))

    # book info
    info_parser = subparser.add_parser('info', help=_('Show book info'))
    info_parser.add_argument('book', help=_('Book'))

    # book list
    list_parser = subparser.add_parser('list', help=_('List books'))
    list_parser.add_argument('--shelf', choices=['read', 'unread'],
                             help=_('Filter books by shelves'))
    list_parser.add_argument('--search', help=_('Filter books by term'))


def edition_subparser(parser):
    edition_parser = parser.add_parser('edition', help=_('Manage editions'))
    edition_parser.add_argument('book', help=_('Book'))
    subparser = edition_parser.add_subparsers(dest='edition_subparser')

    acquisition_subparser(subparser, 'edition', _('Edition'))
    read_subparser(subparser, 'edition', _('Edition'))

    # edition add
    add_parser = subparser.add_parser('add', help=_('Add an edition'))
    add_parser.add_argument('--alternate_title', help=_('Alternate title'))
    add_parser.add_argument('--isbn', help=_('ISBN'))
    add_parser.add_argument('--publishing-date', type=valid_date,
                            help=_('Publishing date'))
    add_parser.add_argument('--cover', help=_('Cover image'))
    add_parser.add_argument('--binding', help=_('Binding'))
    add_parser.add_argument('--publisher', help=_('Publisher'))
    add_parser.add_argument('--file', nargs='*', default=[], help=_('Files'))
    add_parser.add_argument('--language', nargs='*', default=[],
                            help=_('Languages'))

    # edition edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a edition'))
    edit_parser.add_argument('edition', help=_('Edition'))
    edit_subparser = edit_parser.add_subparsers(dest='edit_subparser',
                                                help=_('Which field to edit'))

    edit_edition_parser = edit_subparser.add_parser('alternate_title')
    edit_edition_parser.add_argument('value', help=_('New value for field'))

    edit_edition_parser = edit_subparser.add_parser('isbn')
    edit_edition_parser.add_argument('value', help=_('New value for field'))

    edit_published_parser = edit_subparser.add_parser('publishing-date')
    edit_published_parser.add_argument('value', type=valid_date,
                                       help=_('New value for field'))

    edit_cover_parser = edit_subparser.add_parser('cover')
    edit_cover_parser.add_argument('value', help=_('New value for field'))

    edit_binding_parser = edit_subparser.add_parser('binding')
    edit_binding_parser.add_argument('value', help=_('New value for field'))

    edit_publisher_parser = edit_subparser.add_parser('publisher')
    edit_publisher_parser.add_argument('value', help=_('New value for field'))

    edit_language_parser = edit_subparser.add_parser('language')
    edit_language_parser.add_argument('value', help=_('New value for field'))

    edit_file_parser = edit_subparser.add_parser('file')
    edit_file_parser.add_argument('value', help=_('New value for field'))

    # edition info
    info_parser = subparser.add_parser('info', help=_('Show edition info'))
    info_parser.add_argument('edition', help=_('Edition'))

    # edition list
    list_parser = subparser.add_parser('list', help=_('List editions'))
    list_parser.add_argument('--shelf', choices=['read', 'unread'],
                             help=_('Filter editions by shelf'))
    list_parser.add_argument('--search', help=_('Filter editions by term'))

    # paper open
    help_txt=_('Open a file associated with an edition')
    open_parser = subparser.add_parser('open', help=help_txt)
    open_parser.add_argument('edition', nargs='?', help=_('Edition'))
    open_parser.add_argument('file', type=int, help=_('File to open'))