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
from persons.models import Person
from typing import Optional, TextIO


def _person(args: Namespace, file: TextIO = sys.stdout):
    person: Optional[Person] = None
    if args.subparser == "add":
        person, created = Person.from_dict(
            {"name": args.name, "links": [{"name": link} for link in args.link]}
        )
        if created:
            stdout.write(
                _(f'Successfully added person "{person.name}" with id "{person.id}".'),
                "=",
                file=file,
            )
            person.print(file)
        else:
            stdout.write(
                _(
                    f'The person "{person.name}" already exists with id "{person.id}", '
                    + "aborting..."
                ),
                "",
                file=file,
            )
    elif args.subparser == "delete":
        person = Person.get(args.person)
        if person:
            person.delete()
            stdout.write(
                _(f'Successfully deleted person with id "{person.id}".'),
                "",
                file=file,
            )
        else:
            stdout.write(_("No person found."), "", file=file)
    elif args.subparser == "edit":
        person = Person.get(args.person)
        if person:
            person.edit(args.field, args.value)
            stdout.write(
                _(f'Successfully edited person "{person.name}" with id "{person.id}".'),
                "",
                file=file,
            )
            person.print(file)
        else:
            stdout.write(_("No person found."), "", file=file)
    elif args.subparser == "info":
        person = Person.get(args.person)
        if person:
            person.print(file)
        else:
            stdout.write(_("No person found."), "", file=file)
    elif args.subparser == "list":
        if args.search:
            persons = Person.search(args.search)
        else:
            persons = Person.objects.all()
        stdout.write(
            [
                _("Id"),
                _("Name"),
                _("Number of books"),
                _("Number of editions"),
                _("Number of papers"),
            ],
            "=",
            [0.05, 0.4, 0.6, 0.8],
            file=file,
        )
        for i, has_next in lookahead(persons):
            stdout.write(
                [i.id, i.name, i.books.count(), i.editions.count(), i.papers.count()],
                "_" if has_next else "=",
                [0.05, 0.4, 0.6, 0.8],
                file=file,
            )


def add_subparser(parser: _SubParsersAction):
    """Add subparser for the persons module."""
    person_parser = parser.add_parser("person", help=_("Manage persons"))
    person_parser.set_defaults(func=_person)
    subparser = person_parser.add_subparsers(dest="subparser")

    # person add
    add_parser = subparser.add_parser("add", help=_("Add a person"))
    add_parser.add_argument("name", help=_("Name"))
    add_parser.add_argument("--link", nargs="*", default=[], help=_("Links"))

    # binding delete
    delete_parser = subparser.add_parser("delete", help=_("Delete a person"))
    delete_parser.add_argument("person", help=_("Person"))

    # person edit
    edit_parser = subparser.add_parser("edit", help=_("Edit a person"))
    edit_parser.add_argument("person", help=_("Person"))
    edit_parser.add_argument(
        "field", choices=["name", "link"], help=_("Which field to edit")
    )
    edit_parser.add_argument("value", help=_("New value for field"))

    # person info
    info_parser = subparser.add_parser("info", help=_("Show person info"))
    info_parser.add_argument("person", help=_("Person"))

    # person list
    list_parser = subparser.add_parser("list", help=_("List persons"))
    list_parser.add_argument("--search", help=_("Filter persons by term"))
