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
"""Persons Django app argparse."""

import sys

from argparse import _SubParsersAction, Namespace
from bibliothek import stdout
from bibliothek.utils import lookahead
from django.utils.translation import gettext_lazy as _
from links.models import Link
from persons.models import Person
from typing import Optional, TextIO


def _person(args: Namespace, file: TextIO = sys.stdout):
    person: Optional[Person] = None
    if args.subparser == "add":
        person, created = Person.from_dict(
            {
                "name": args.name,
                "links": [Link.get_or_create(link).to_dict() for link in args.link],
            }
        )
        if created:
            stdout.write(
                _('Successfully added person "%(name)s" with id "%(pk)d".')
                % {"name": person.name, "pk": person.pk},
                "=",
                file=file,
            )
            person.print(file)
        else:
            stdout.write(
                _('The person "%(name)s" already exists with id "%(pk)d", aborting...')
                % {"name": person.name, "pk": person.pk},
                "",
                file=file,
            )
    elif args.subparser == "delete":
        person = Person.get(args.person)
        if person:
            person.delete()
            stdout.write(_("Successfully deleted person."), "", file=file)
        else:
            stdout.write(_("No person found."), "", file=file)
    elif args.subparser == "edit":
        person = Person.get(args.person)
        if person:
            person.edit(args.field, args.value)
            stdout.write(
                _('Successfully edited person "%(name)s" with id "%(pk)d".')
                % {"name": person.name, "pk": person.pk},
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
