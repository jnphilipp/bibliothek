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

import os
import sys
import utils

from bibliothek.argparse import valid_date
from books.functions import book as fbook, edition as fedition
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from shelves.argparse import acquisition_subparser, read_subparser
from shelves.functions import acquisition as facquisition, read as fread


def _book(args):
    if args.subparser == 'add':
        book, created = fbook.create(args.title, args.author, args.series,
                                     args.volume, args.genre, args.link)

        if created:
            msg = _(f'Successfully added book "{book.title}" with id ' +
                    f'"{book.id}".')
            utils.stdout.p([msg], '=')
            fbook.stdout.info(book)
        else:
            msg = _(f'The book "{book.title}" already exists with id ' +
                    f'"{book.id}", aborting...')
            utils.stdout.p([msg], '')

    elif args.subparser == 'edit':
        book = fbook.get.by_term(args.book)
        if book:
            fbook.edit(book, args.edit_subparser, args.value)
            msg = _(f'Successfully edited book "{book.title}" with id ' +
                    f'"{book.id}".')
            utils.stdout.p([msg], '=')
            fbook.stdout.info(book)
        else:
            utils.stdout.p(['No book found.'], '')
    elif args.subparser == 'edition':
        book = fbook.get.by_term(args.book)
        if book is None:
            utils.stdout.p(['No book found.'], '')
        else:
            if args.edition_subparser == 'acquisition' and book:
                edition = fedition.get.by_term(args.edition, book)
                if args.acquisition_subparser == 'add' and edition:
                    acquisition = facquisition.create(edition, args.date,
                                                      args.price)
                    msg = _('Successfully added acquisition with id ' +
                            f'"{acquisition.id}".')
                    utils.stdout.p([msg], '=')
                    facquisition.stdout.info(acquisition)
                elif args.acquisition_subparser == 'delete' and edition:
                    acquisition = facquisition.get.by_pk(args.acquisition,
                                                         edition=edition)
                    if acquisition:
                        facquisition.delete(acquisition)
                        msg = _('Successfully deleted acquisition with id ' +
                                f'"{acquisition.id}".')
                        utils.stdout.p([msg], '')
                    else:
                        utils.stdout.p(['No acquisition found.'], '')
                elif args.acquisition_subparser == 'edit' and edition:
                    acquisition = facquisition.get.by_pk(args.acquisition,
                                                         edition=edition)
                    if acquisition:
                        facquisition.edit(acquisition, args.field, args.value)
                        msg = _('Successfully edited acquisition with id ' +
                                f'"{acquisition.id}".')
                        utils.stdout.p([msg], '=')
                        facquisition.stdout.info(acquisition)
                    else:
                        utils.stdout.p(['No acquisition found.'], '')
                else:
                    utils.stdout.p(['No edition found.'], '')
            elif args.edition_subparser == 'add' and book:
                edition, created = fedition.create(book, args.alternate_title,
                                                   args.isbn,
                                                   args.publishing_date,
                                                   args.cover, args.binding,
                                                   args.publisher, args.person,
                                                   args.language, args.link,
                                                   args.file)
                if created:
                    msg = _(f'Successfully added edition "{edition}" with id' +
                            f' "{edition.id}".')
                    utils.stdout.p([msg], '=')
                    fedition.stdout.info(edition)
                else:
                    msg = _(f'The edition "{edition}" already exists with id' +
                            f' "{edition.id}", aborting...')
                    stdout.p([msg], '')
            elif args.edition_subparser == 'edit' and book:
                edition = fedition.get.by_term(args.edition, book)
                if edition:
                    fedition.edit(edition, args.edit_subparser, args.value)
                    msg = _(f'Successfully edited edition "{edition}" with ' +
                            f'id "{edition.id}".')
                    utils.stdout.p([msg], '=')
                    fedition.stdout.info(edition)
                else:
                    utils.stdout.p(['No edition found.'], '')
            elif args.edition_subparser == 'info' and book:
                edition = fedition.get.by_term(args.edition, book)
                if edition:
                    fedition.stdout.info(edition)
                else:
                    utils.stdout.p(['No edition found.'], '')
            elif args.edition_subparser == 'list' and book:
                if args.shelf:
                    editions = fedition.list.by_shelf(args.shelf, book)
                elif args.search:
                    editions = fedition.list.by_term(args.search, book)
                else:
                    editions = fedition.list.all(book)
                fedition.stdout.list(editions)
            elif args.edition_subparser == 'open' and book:
                edition = fedition.get.by_term(args.edition, book)
                if edition:
                    file = edition.files.get(pk=args.file)
                    path = os.path.join(settings.MEDIA_ROOT, file.file.path)
                    if sys.platform == 'linux':
                        os.system('xdg-open "%s"' % path)
                    else:
                        os.system('open "%s"' % path)
                else:
                    utils.stdout.p(['No edition found.'], '')
            elif args.edition_subparser == 'read' and book:
                edition = fedition.get.by_term(args.edition, book)
                if args.read_subparser == 'add' and edition:
                    read = fread.create(edition, args.started, args.finished)
                    msg = _(f'Successfully added read with id "{read.id}".')
                    utils.stdout.p([msg], '=')
                    fread.stdout.info(read)
                elif args.read_subparser == 'delete' and edition:
                    read = fread.get.by_pk(args.read, edition=edition)
                    if read:
                        fread.delete(read)
                        msg = _('Successfully deleted read with id ' +
                                f'"{read.id}".')
                        utils.stdout.p([msg], '')
                    else:
                        utils.stdout.p(['No read found.'], '')
                elif args.read_subparser == 'edit' and edition:
                    read = fread.get.by_pk(args.read, edition=edition)
                    if read:
                        fread.edit(read, args.field, args.value)
                        msg = _('Successfully edited read with id ' +
                                f'"{read.id}".')
                        utils.stdout.p([msg], '=')
                        fread.stdout.info(read)
                    else:
                        utils.stdout.p(['No read found.'], '')
                else:
                    utils.stdout.p(['No edition found.'], '')
    elif args.subparser == 'info':
        book = fbook.get.by_term(args.book)
        if book:
            fbook.stdout.info(book)
        else:
            utils.stdout.p(['No book found.'], '')
    elif args.subparser == 'list':
        if args.shelf:
            books = fbook.list.by_shelf(args.shelf)
        elif args.search:
            books = fbook.list.by_term(args.search)
        else:
            books = fbook.list.all()
        fbook.stdout.list(books)


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
    edit_parser.add_argument('book', help='Book')
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
    add_parser.add_argument('--alternate-title', help=_('Alternate title'))
    add_parser.add_argument('--isbn', help=_('ISBN'))
    add_parser.add_argument('--publishing-date', type=valid_date,
                            help=_('Publishing date'))
    add_parser.add_argument('--cover', help=_('Cover image'))
    add_parser.add_argument('--binding', help=_('Binding'))
    add_parser.add_argument('--person', nargs='*', default=[],
                            help=_('Persons'))
    add_parser.add_argument('--publisher', help=_('Publisher'))
    add_parser.add_argument('--file', nargs='*', default=[], help=_('Files'))
    add_parser.add_argument('--language', nargs='*', default=[],
                            help=_('Languages'))
    add_parser.add_argument('--link', nargs='*', default=[],
                            help=_('Links'))

    # edition edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a edition'))
    edit_parser.add_argument('edition', help=_('Edition'))
    edit_subparser = edit_parser.add_subparsers(dest='edit_subparser',
                                                help=_('Which field to edit'))

    edit_edition_parser = edit_subparser.add_parser('alternate-title')
    edit_edition_parser.add_argument('value', help=_('New value for field'))

    edit_edition_parser = edit_subparser.add_parser('isbn')
    edit_edition_parser.add_argument('value', help=_('New value for field'))

    edit_pubdate_parser = edit_subparser.add_parser('publishing-date')
    edit_pubdate_parser.add_argument('value', type=valid_date,
                                     help=_('New value for field'))

    edit_cover_parser = edit_subparser.add_parser('cover')
    edit_cover_parser.add_argument('value', help=_('New value for field'))

    edit_binding_parser = edit_subparser.add_parser('binding')
    edit_binding_parser.add_argument('value', help=_('New value for field'))

    edit_publisher_parser = edit_subparser.add_parser('publisher')
    edit_publisher_parser.add_argument('value', help=_('New value for field'))

    edit_person_parser = edit_subparser.add_parser('person')
    edit_person_parser.add_argument('value', help=_('New value for field'))

    edit_language_parser = edit_subparser.add_parser('language')
    edit_language_parser.add_argument('value', help=_('New value for field'))

    edit_link_parser = edit_subparser.add_parser('link')
    edit_link_parser.add_argument('value', help=_('New value for field'))

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

    # edition open
    help_txt = _('Open a file associated with an edition')
    open_parser = subparser.add_parser('open', help=help_txt)
    open_parser.add_argument('edition', nargs='?', help=_('Edition'))
    open_parser.add_argument('file', type=int, help=_('File to open'))
