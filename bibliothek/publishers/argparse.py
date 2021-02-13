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

from argparse import _SubParsersAction, Namespace
from bibliothek import stdout
from bibliothek.utils import lookahead
from django.utils.translation import ugettext_lazy as _
from publishers.models import Publisher
from typing import Optional, TextIO


def _publisher(args: Namespace, file: TextIO = sys.stdout):
    publishers: Optional[Publisher] = None
    if args.subparser == "add":
        series, created = Publisher.from_dict(
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
        publisher = Publisher.get(args.publisher)
        if publisher:
            publisher.delete()
            stdout.write(
                _(f'Successfully deleted publisher with id "{publisher.id}".'),
                "",
                file=file,
            )
        else:
            stdout.write(_("No publisher found."), "", file=file)
    elif args.subparser == "edit":
        publisher = Publisher.get(args.publisher)
        if publisher:
            publisher.edit(args.field, args.value)
            stdout.write(
                _(
                    f'Successfully edited publisher "{publisher.name}" with id '
                    + f'"{publisher.id}".'
                ),
                "",
                file=file,
            )
            publisher.print(file)
        else:
            stdout.write(_("No publisher found."), "", file=file)
    elif args.subparser == "info":
        publisher = Publisher.get(args.publisher)
        if publisher:
            publisher.print(file)
        else:
            stdout.write(_("No publisher found."), "", file=file)
    elif args.subparser == "list":
        if args.search:
            publishers = Publisher.search(args.search)
        else:
            publishers = Publisher.objects.all()
        stdout.write(
            [_("Id"), _("Name"), _("Number of editions")], "=", [0.05, 0.8], file=file
        )
        for i, has_next in lookahead(publishers):
            stdout.write(
                [i.id, i.name, i.editions.count()],
                "_" if has_next else "=",
                [0.05, 0.8],
                file=file,
            )


def add_subparser(parser: _SubParsersAction):
    """Add subparser for the publishers module."""
    publisher_parser = parser.add_parser("publisher", help=_("Manage publishers"))
    publisher_parser.set_defaults(func=_publisher)
    subparser = publisher_parser.add_subparsers(dest="subparser")

    # publisher add
    add_parser = subparser.add_parser("add", help=_("Add a publisher"))
    add_parser.add_argument("name", help=_("Name"))
    add_parser.add_argument("--link", nargs="*", default=[], help=_("Links"))

    # publisher delete
    delete_parser = subparser.add_parser("delete", help=_("Delete a publisher"))
    delete_parser.add_argument("publisher", help=_("Publisher"))

    # publisher edit
    edit_parser = subparser.add_parser("edit", help=_("Edit a publisher"))
    edit_parser.add_argument("publisher", help=_("Publisher"))
    edit_parser.add_argument(
        "field", choices=["name", "link"], help=_("Which field to edit")
    )
    edit_parser.add_argument("value", help=_("New value for field"))

    # publisher info
    info_parser = subparser.add_parser("info", help=_("Show publisher info"))
    info_parser.add_argument("publisher", help=_("Publisher"))

    # publisher list
    list_parser = subparser.add_parser("list", help=_("List publishers"))
    list_parser.add_argument("--search", help=_("Filter publishers by term"))
