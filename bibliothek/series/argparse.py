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


import sys

from bibliothek import stdout
from bibliothek.utils import lookahead
from django.utils.translation import ugettext_lazy as _
from series.models import Series
from typing import Optional, TextIO


def _series(args, file: TextIO = sys.stdout):
    series: Optional[Series] = None
    if args.subparser == "add":
        series, created = Series.from_dict(
            {"name": args.name, "links": [{"name": link} for link in args.link]}
        )
        if created:
            stdout.write(
                _(f'Successfully added series "{series.name}" with id "{series.id}".'),
                "=",
                file=file,
            )
            series.print(file)
        else:
            stdout.write(
                _(
                    f'The series "{series.name}" already exists with id "{series.id}", '
                    + "aborting..."
                ),
                "",
                file=file,
            )
    elif args.subparser == "delete":
        series = Series.get(args.series)
        if series:
            series.delete()
            stdout.write(
                _(f'Successfully deleted series with id "{series.id}".'),
                "",
                file=file,
            )
        else:
            stdout.write(_("No series found."), "", file=file)
    elif args.subparser == "edit":
        series = Series.get(args.series)
        if series:
            series.edit(args.field, args.value)
            stdout.write(
                _(f'Successfully edited series "{series.name}" with id "{series.id}".'),
                "",
                file=file,
            )
            series.print(file)
        else:
            stdout.write(_("No series found."), "", file=file)
    elif args.subparser == "info":
        series = Series.get(args.series)
        if series:
            series.print(file)
        else:
            stdout.write(_("No series found."), "", file=file)
    elif args.subparser == "list":
        if args.search:
            bindings = Series.search(args.search)
        else:
            bindings = Series.objects.all()
        stdout.write(
            [_("Id"), _("Name"), _("Number of books")], "=", [0.05, 0.8], file=file
        )
        for i, has_next in lookahead(bindings):
            stdout.write(
                [i.id, i.name, i.books.count()],
                "_" if has_next else "=",
                [0.05, 0.8],
                file=file,
            )


def add_subparser(parser):
    """Add subparser for the series module."""
    series_parser = parser.add_parser("series", help=_("Manage series"))
    series_parser.set_defaults(func=_series)
    subparser = series_parser.add_subparsers(dest="subparser")

    # series add
    add_parser = subparser.add_parser("add", help=_("Add a new series"))
    add_parser.add_argument("name", help=_("Name"))
    add_parser.add_argument("--link", nargs="*", default=[], help=_("Links"))

    # binding delete
    delete_parser = subparser.add_parser("delete", help=_("Delete a series"))
    delete_parser.add_argument("series", help=_("Series"))

    # series edit
    edit_parser = subparser.add_parser("edit", help=_("Edit a series"))
    edit_parser.add_argument("series", help=_("Series"))
    edit_parser.add_argument(
        "field", choices=["name", "link"], help=_("Which field to edit")
    )
    edit_parser.add_argument("value", help=_("New value for field"))

    # series info
    info_parser = subparser.add_parser("info", help=_("Show series info"))
    info_parser.add_argument("series", help=_("Series"))

    # series list
    list_parser = subparser.add_parser("list", help=_("List series"))
    list_parser.add_argument("--search", help=_("Filter series by term"))
