# -*- coding: utf-8 -*-
# Copyright (C) 2016-2021 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Books Django app argparse."""

import os
import sys

from argparse import _SubParsersAction, Namespace
from bibliothek import stdout
from bibliothek.utils import lookahead
from bibliothek.argparse import valid_date
from bindings.models import Binding
from books.models import Book, Edition
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from genres.models import Genre
from languages.models import Language
from links.models import Link
from persons.models import Person
from publishers.models import Publisher
from series.models import Series
from shelves.models import Acquisition, Read
from shelves.argparse import acquisition_subparser, read_subparser
from typing import Optional, TextIO


def _book(args: Namespace, file: TextIO = sys.stdout):
    book: Optional[Book] = None
    if args.subparser == "add":
        book, created = Book.from_dict(
            {
                "title": args.title,
                "authors": [
                    Person.get_or_create(author).to_dict() for author in args.author
                ],
                "series": Series.get_or_create(args.series).to_dict()
                if args.series
                else None,
                "volume": args.volume,
                "genres": [
                    Genre.get_or_create(genre).to_dict() for genre in args.genre
                ],
                "links": [Link.get_or_create(link).to_dict() for link in args.link],
            }
        )

        if created:
            stdout.write(
                _('Successfully added book "%(title)s" with id "%(pk)d".')
                % {"title": book.title, "pk": book.pk},
                "=",
                file=file,
            )
            book.print(file)
        else:
            stdout.write(
                _('The book "%(title)s" already exists with id "%(pk)d", aborting...')
                % {"title": book.title, "pk": book.pk},
                "",
                file=file,
            )
    elif args.subparser == "delete":
        book = Book.get(args.book)
        if book:
            book.delete()
            stdout.write(
                _('Successfully deleted book "%(title)s" with id "%(pk)d".')
                % {"title": book.title, "pk": book.pk},
                "",
                file=file,
            )
        else:
            stdout.write(_("No book found."), "", file=file)
    elif args.subparser == "edit":
        book = Book.get(args.book)
        if book:
            book.edit(args.edit_subparser, args.value)
            stdout.write(
                _('Successfully edited book "%(title)s" with id "%(pk)d".')
                % {"title": book.title, "pk": book.pk},
                "=",
                file=file,
            )
            book.print(file)
        else:
            stdout.write(_("No book found."), "", file=file)
    elif args.subparser == "edition":
        book = Book.get(args.book)
        if book:
            if args.edition_subparser == "acquisition" and book:
                edition = Edition.get(args.edition, book)
                acquisition: Optional[Acquisition] = None
                if args.acquisition_subparser == "add" and edition:
                    acquisition, created = Acquisition.from_dict(
                        {"date": args.date, "price": args.price}, edition
                    )
                    if created:
                        stdout.write(
                            _('Successfully added acquisition with id "%(pk)d".')
                            % {"pk": acquisition.pk},
                            "=",
                            file=file,
                        )
                    else:
                        stdout.write(
                            _('The acquisition already exists with id "%(pk)d".')
                            % {"pk": acquisition.pk},
                            "",
                            file=file,
                        )
                    acquisition.print(file)
                elif args.acquisition_subparser == "delete" and edition:
                    acquisition = Acquisition.get(args.acquisition, editions=edition)
                    if acquisition:
                        acquisition.delete(acquisition)
                        stdout.write(
                            _('Successfully deleted acquisition with id "%(pk)d".')
                            % {"pk": acquisition.pk},
                            "",
                            file=file,
                        )
                    else:
                        stdout.write(_("No acquisition found."), "", file=file)
                elif args.acquisition_subparser == "edit" and edition:
                    acquisition = Acquisition.get(args.acquisition, editions=edition)
                    if acquisition:
                        acquisition.edit(args.field, args.value)
                        stdout.write(
                            _('Successfully edited acquisition with id "%(pk)d".')
                            % {"pk": acquisition.pk},
                            "=",
                            file=file,
                        )
                        acquisition.print(file)
                    else:
                        stdout.write(_("No acquisition found."), "", file=file)
                else:
                    stdout.write([_("No edition found.")], "", file=file)
            elif args.edition_subparser == "add" and book:
                edition, created = Edition.from_dict(
                    {
                        "alternate_title": args.alternate_title,
                        "isbn": args.isbn,
                        "publishing_date": args.publishing_date,
                        "cover": args.cover,
                        "binding": Binding.get_or_create(args.binding).to_dict()
                        if args.binding
                        else None,
                        "publisher": Publisher.get_or_create(args.publisher).to_dict()
                        if args.publisher
                        else None,
                        "persons": [
                            Person.get_or_create(person).to_dict()
                            for person in args.person
                        ],
                        "languages": [
                            Language.get_or_create(language).to_dict()
                            for language in args.language
                        ],
                        "links": [
                            Link.get_or_create(link).to_dict() for link in args.link
                        ],
                        "files": [{"path": file} for file in args.file],
                    },
                    book,
                )
                if created:
                    stdout.write(
                        _('Successfully added edition "%(edition)s" with id "%(pk)d".')
                        % {"edition": edition, "pk": edition.pk},
                        "=",
                        file=file,
                    )
                    edition.print(file)
                else:
                    stdout.write(
                        _(
                            'The edition "%(edition)s" already exists with id "%(pk)d",'
                            + " aborting..."
                        )
                        % {"edition": edition, "pk": edition.pk},
                        "",
                        file=file,
                    )
            elif args.edition_subparser == "edit" and book:
                edition = Edition.get(args.edition, book)
                if edition:
                    edition.edit(args.edit_subparser, args.value)
                    stdout.write(
                        _('Successfully edited edition "%(edition)s" with id "%(pk)d".')
                        % {"edition": edition, "pk": edition.pk},
                        "=",
                        file=file,
                    )
                    edition.print(file)
                else:
                    stdout.write(_("No edition found."), "", file=file)
            elif args.edition_subparser == "info" and book:
                edition = Edition.get(args.edition, book)
                if edition:
                    edition.print(file)
                else:
                    stdout.write(_("No edition found."), "", file=file)
            elif args.edition_subparser == "list" and book:
                if args.shelf:
                    editions = Edition.list.by_shelf(args.shelf, book)
                elif args.search:
                    editions = Edition.list.by_term(args.search, book)
                else:
                    editions = Edition.objects.filter(book=book)
                stdout.write(
                    [
                        _("Id"),
                        _("Title"),
                        _("Binding"),
                        _("ISBN"),
                        _("Publishing date"),
                    ],
                    "=",
                    [0.05, 0.55, 0.7, 0.85],
                    file=file,
                )
                for i, has_next in lookahead(editions):
                    stdout.write(
                        [i.pk, i.get_title(), i.binding, i.isbn, i.publishing_date],
                        "_" if has_next else "=",
                        [0.05, 0.55, 0.7, 0.85],
                        file=file,
                    )
            elif args.edition_subparser == "open" and book:
                edition = Edition.get(args.edition, book)
                if edition:
                    edition_file = edition.files.get(pk=args.file)
                    path = settings.MEDIA_ROOT / edition_file.file.path
                    if sys.platform == "linux":
                        os.system(f'xdg-open "{path}"')
                    else:
                        os.system(f'open "{path}"')
                else:
                    stdout.write(_("No edition found."), "", file=file)
            elif args.edition_subparser == "read" and book:
                edition = Edition.get(args.edition, book)
                read: Optional[Read] = None
                if args.read_subparser == "add" and edition:
                    read, created = Read.from_dict(
                        {"started": args.started, "finished": args.finished}, edition
                    )
                    if created:
                        stdout.write(
                            _('Successfully added read with id "%(pk)d".')
                            % {"pk": read.pk},
                            "=",
                            file=file,
                        )
                    else:
                        stdout.write(
                            _('The read already exists with id "%(pk)d".')
                            % {"pk": read.pk},
                            "",
                            file=file,
                        )
                    read.print(file)
                elif args.read_subparser == "delete" and edition:
                    read = Read.get(args.read, editions=edition)
                    if read:
                        read.delete()
                        stdout.write(
                            _('Successfully deleted read with id "%(pk)d".')
                            % {"pk": read.pk},
                            "",
                            file=file,
                        )
                    else:
                        stdout.write(_("No read found."), "", file=file)
                elif args.read_subparser == "edit" and edition:
                    read = Read.get(args.read, editions=edition)
                    if read:
                        read.edit(args.field, args.value)
                        stdout.write(
                            _('Successfully edited read with id "%(pk)d".')
                            % {"pk": read.pk},
                            "=",
                            file=file,
                        )
                        read.info(file)
                    else:
                        stdout.write(_("No read found."), "", file=file)
                else:
                    stdout.write(_("No edition found."), "", file=file)
        else:
            stdout.write(_("No book found."), "", file=file)
    elif args.subparser == "info":
        book = Book.get(args.book)
        if book:
            book.print(file)
        else:
            stdout.write(_("No book found."), "", file=file)
    elif args.subparser == "list":
        if args.search:
            books = Book.search(args.search)
        elif args.shelf:
            books = Book.by_shelf(args.shelf)
        else:
            books = Book.objects.all()
        stdout.write(
            [_("Id"), ("Title"), _("Authors"), _("Series"), _("Volume")],
            "=",
            [0.05, 0.5, 0.75, 0.9],
            file=file,
        )
        for i, has_next in lookahead(books):
            stdout.write(
                [
                    i.pk,
                    i.title,
                    " ,".join(f"{a}" for a in i.authors.all()),
                    i.series.name if i.series else "",
                    i.volume,
                ],
                "_" if has_next else "=",
                [0.05, 0.5, 0.75, 0.9],
                file=file,
            )


def add_subparser(parser: _SubParsersAction):
    """Add subparser for the Book model."""
    book_parser = parser.add_parser("book", help=_("Manage books"))
    book_parser.set_defaults(func=_book)
    subparser = book_parser.add_subparsers(dest="subparser")
    edition_subparser(subparser)

    # book add
    add_parser = subparser.add_parser("add", help=_("Add a book"))
    add_parser.add_argument("title", help=_("Title"))
    add_parser.add_argument("--author", nargs="*", default=[], help=_("Authors"))
    add_parser.add_argument("--series", default=None, help=_("Series"))
    add_parser.add_argument(
        "--volume", default=None, type=float, help=_("Series volume")
    )
    add_parser.add_argument("--genre", nargs="*", default=[], help=_("Genres"))
    add_parser.add_argument("--link", nargs="*", default=[], help=_("Links"))

    # book edit
    edit_parser = subparser.add_parser("edit", help=_("Edit a book"))
    edit_parser.add_argument("book", help="Book")
    edit_subparser = edit_parser.add_subparsers(
        dest="edit_subparser", help=_("Which field to edit")
    )

    edit_title_parser = edit_subparser.add_parser("title")
    edit_title_parser.add_argument("value", help=_("New value for field"))

    edit_author_parser = edit_subparser.add_parser("author")
    edit_author_parser.add_argument("value", help=_("New value for field"))

    edit_series_parser = edit_subparser.add_parser("series")
    edit_series_parser.add_argument("value", help=_("New value for field"))

    edit_volume_parser = edit_subparser.add_parser("volume")
    edit_volume_parser.add_argument("value", type=float, help=_("New value for field"))

    edit_genre_parser = edit_subparser.add_parser("genre")
    edit_genre_parser.add_argument("value", help=_("New value for field"))

    edit_link_parser = edit_subparser.add_parser("link")
    edit_link_parser.add_argument("value", help=_("New value for field"))

    # book info
    info_parser = subparser.add_parser("info", help=_("Show book info"))
    info_parser.add_argument("book", help=_("Book"))

    # book list
    list_parser = subparser.add_parser("list", help=_("List books"))
    list_parser.add_argument(
        "--shelf", choices=["read", "unread"], help=_("Filter books by shelves")
    )
    list_parser.add_argument("--search", help=_("Filter books by term"))


def edition_subparser(parser: _SubParsersAction):
    """Add subparser for the Book model."""
    edition_parser = parser.add_parser("edition", help=_("Manage editions"))
    edition_parser.add_argument("book", help=_("Book"))
    subparser = edition_parser.add_subparsers(dest="edition_subparser")
    acquisition_subparser(subparser, "edition", _("Edition"))
    read_subparser(subparser, "edition", _("Edition"))

    # edition add
    add_parser = subparser.add_parser("add", help=_("Add an edition"))
    add_parser.add_argument("--alternate-title", help=_("Alternate title"))
    add_parser.add_argument("--isbn", help=_("ISBN"))
    add_parser.add_argument(
        "--publishing-date", type=valid_date, help=_("Publishing date")
    )
    add_parser.add_argument("--cover", help=_("Cover image"))
    add_parser.add_argument("--binding", help=_("Binding"))
    add_parser.add_argument("--person", nargs="*", default=[], help=_("Persons"))
    add_parser.add_argument("--publisher", help=_("Publisher"))
    add_parser.add_argument("--file", nargs="*", default=[], help=_("Files"))
    add_parser.add_argument("--language", nargs="*", default=[], help=_("Languages"))
    add_parser.add_argument("--link", nargs="*", default=[], help=_("Links"))

    # edition edit
    edit_parser = subparser.add_parser("edit", help=_("Edit a edition"))
    edit_parser.add_argument("edition", help=_("Edition"))
    edit_subparser = edit_parser.add_subparsers(
        dest="edit_subparser", help=_("Which field to edit")
    )

    edit_edition_parser = edit_subparser.add_parser("alternate-title")
    edit_edition_parser.add_argument("value", help=_("New value for field"))

    edit_edition_parser = edit_subparser.add_parser("isbn")
    edit_edition_parser.add_argument("value", help=_("New value for field"))

    edit_pubdate_parser = edit_subparser.add_parser("publishing-date")
    edit_pubdate_parser.add_argument(
        "value", type=valid_date, help=_("New value for field")
    )

    edit_cover_parser = edit_subparser.add_parser("cover")
    edit_cover_parser.add_argument("value", help=_("New value for field"))

    edit_binding_parser = edit_subparser.add_parser("binding")
    edit_binding_parser.add_argument("value", help=_("New value for field"))

    edit_publisher_parser = edit_subparser.add_parser("publisher")
    edit_publisher_parser.add_argument("value", help=_("New value for field"))

    edit_person_parser = edit_subparser.add_parser("person")
    edit_person_parser.add_argument("value", help=_("New value for field"))

    edit_language_parser = edit_subparser.add_parser("language")
    edit_language_parser.add_argument("value", help=_("New value for field"))

    edit_link_parser = edit_subparser.add_parser("link")
    edit_link_parser.add_argument("value", help=_("New value for field"))

    edit_file_parser = edit_subparser.add_parser("file")
    edit_file_parser.add_argument("value", help=_("New value for field"))

    # edition info
    info_parser = subparser.add_parser("info", help=_("Show edition info"))
    info_parser.add_argument("edition", help=_("Edition"))

    # edition list
    list_parser = subparser.add_parser("list", help=_("List editions"))
    list_parser.add_argument(
        "--shelf", choices=["read", "unread"], help=_("Filter editions by shelf")
    )
    list_parser.add_argument("--search", help=_("Filter editions by term"))

    # edition open
    help_txt = _("Open a file associated with an edition")
    open_parser = subparser.add_parser("open", help=help_txt)
    open_parser.add_argument("edition", nargs="?", help=_("Edition"))
    open_parser.add_argument("file", type=int, help=_("File to open"))
