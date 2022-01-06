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
"""Journals Django app argparse."""

import sys

from argparse import _SubParsersAction, Namespace
from bibliothek import stdout
from bibliothek.utils import lookahead
from django.utils.translation import gettext_lazy as _
from journals.models import Journal
from links.models import Link
from typing import Optional, TextIO


def _journal(args: Namespace, file: TextIO = sys.stdout):
    journal: Optional[Journal] = None
    if args.subparser == "add":
        journal, created = Journal.from_dict(
            {
                "name": args.name,
                "links": [Link.get_or_create(link).to_dict() for link in args.link],
            }
        )
        if created:
            stdout.write(
                _('Successfully added journal "%(name)s" with id "%(pk)d".')
                % {"name": journal.name, "pk": journal.pk},
                "=",
                file=file,
            )
            journal.print(file)
        else:
            stdout.write(
                _('The journal "%(name)s" already exists with id "%(pk)d", aborting...')
                % {"name": journal.name, "pk": journal.pk},
                "",
                file=file,
            )
    elif args.subparser == "delete":
        journal = Journal.get(args.journal)
        if journal:
            journal.delete()
            stdout.write(
                _('Successfully deleted journal with id "%(pk)d".')
                % {"pk": journal.pk},
                "",
                file=file,
            )
        else:
            stdout.write(_("No journal found."), "", file=file)
    elif args.subparser == "edit":
        journal = Journal.get(args.journal)
        if journal:
            journal.edit(args.field, args.value)
            stdout.write(
                _('Successfully edited journal "%(name)s" with id "%(pk)d".')
                % {"name": journal.name, "pk": journal.pk},
                "",
                file=file,
            )
            journal.print(file)
        else:
            stdout.write(_("No journal found."), "", file=file)
    elif args.subparser == "info":
        journal = Journal.get(args.journal)
        if journal:
            journal.info(file)
        else:
            stdout.write([_("No journal found.")], "")
    elif args.subparser == "list":
        if args.search:
            journals = Journal.search(args.search)
        else:
            journals = Journal.objects.all()
        stdout.write(
            [_("Id"), _("Name"), _("Number of papers")], "=", [0.05, 0.8], file=file
        )
        for i, has_next in lookahead(journals):
            stdout.write(
                [i.id, i.name, i.papers.count()],
                "_" if has_next else "=",
                [0.05, 0.8],
                file=file,
            )


def add_subparser(parser: _SubParsersAction):
    """Add subparser for the journals module."""
    journal_parser = parser.add_parser("journal", help=_("Manage journals"))
    journal_parser.set_defaults(func=_journal)
    subparser = journal_parser.add_subparsers(dest="subparser")

    # journal add
    add_parser = subparser.add_parser("add", help=_("Add a journal"))
    add_parser.add_argument("name", help="name")
    add_parser.add_argument("--link", nargs="*", default=[], help=_("Links"))

    # journal delete
    delete_parser = subparser.add_parser("delete", help=_("Delete a journal"))
    delete_parser.add_argument("journal", help=_("Journal"))

    # journal edit
    edit_parser = subparser.add_parser("edit", help=_("Edit a journal"))
    edit_parser.add_argument("journal", help=_("Journal"))
    edit_parser.add_argument(
        "field", choices=["name", "link"], help=_("Which field to edit")
    )
    edit_parser.add_argument("value", help=_("New value for field"))

    # journal info
    info_parser = subparser.add_parser("info", help=_("Show journal info"))
    info_parser.add_argument("journal", help=_("Journal"))

    # journal list
    list_parser = subparser.add_parser("list", help=_("List journals"))
    list_parser.add_argument("--search", help=_("Filter journals by term"))
