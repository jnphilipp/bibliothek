# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2016-2022 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Genres Django app argparse."""

import sys

from bibliothek import stdout
from bibliothek.utils import lookahead
from django.utils.translation import gettext_lazy as _
from genres.models import Genre
from typing import Optional, TextIO


def _genre(args, file: TextIO = sys.stdout):
    genre: Optional[Genre] = None
    if args.subparser == "add":
        genre, created = Genre.from_dict({"name": args.name})
        if created:
            stdout.write(
                _('Successfully added genre "%(name)s" with id "%(pk)d".')
                % {"name": genre.name, "pk": genre.pk},
                "=",
            )
            genre.print(file)
        else:
            stdout.write(
                _('The genre "%(name)s" already exists with id "%(pk)d", aborting...')
                % {"name": genre.name, "pk": genre.pk},
                "",
            )
    elif args.subparser == "delete":
        genre = Genre.get(args.genre)
        if genre:
            genre.delete()
            stdout.write(
                _('Successfully deleted genre with id "%(pk)d".') % {"pk": genre.pk}, ""
            )
        else:
            stdout.write(_("No genre found."), "")
    elif args.subparser == "edit":
        genre = Genre.get(args.genre)
        if genre:
            genre.edit(args.field, args.value)
            stdout.write(
                _('Successfully edited genre "%(name)s" with id "%(pk)d".')
                % {"name": genre.name, "pk": genre.pk},
                "",
            )
            genre.print(file)
        else:
            stdout.write(_("No genre found."), "")
    elif args.subparser == "info":
        genre = Genre.get(args.genre)
        if genre:
            genre.print(file)
        else:
            stdout.write(_("No genre found."), "")
    elif args.subparser == "list":
        if args.search:
            genres = Genre.search(args.search)
        else:
            genres = Genre.objects.all()
        stdout.write([_("Id"), _("Name")], "=", [0.05], file=file)
    for i, has_next in lookahead(genres):
        stdout.write([i.id, i.name], "_" if has_next else "=", [0.05], file=file)


def add_subparser(parser):
    """Add subparser for the genres module."""
    genre_parser = parser.add_parser("genre", help=_("Manage genres"))
    genre_parser.set_defaults(func=_genre)
    subparser = genre_parser.add_subparsers(dest="subparser")

    # genre add
    add_parser = subparser.add_parser("add", help=_("Add a genre"))
    add_parser.add_argument("name", help=_("Name"))

    # genre delete
    delete_parser = subparser.add_parser("delete", help=_("Delete a genre"))
    delete_parser.add_argument("genre", help=_("Genre"))

    # genre edit
    edit_parser = subparser.add_parser("edit", help=_("Edit a genre"))
    edit_parser.add_argument("genre", help=_("Genre"))
    edit_parser.add_argument("field", choices=["name"], help=_("Which field to edit"))
    edit_parser.add_argument("value", help=_("New value for field"))

    # genre info
    info_parser = subparser.add_parser("info", help=_("Show genre info"))
    info_parser.add_argument("genre", help=_("Genre"))

    # genre list
    list_parser = subparser.add_parser("list", help=_("List genres"))
    list_parser.add_argument("--search", help=_("Filter genres by term"))
