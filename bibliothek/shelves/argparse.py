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
"""Shelves argparse."""

import sys

from argparse import _SubParsersAction, Namespace
from bibliothek import stdout
from bibliothek.argparse import valid_date
from books.models import Edition
from django.utils.translation import gettext_lazy as _
from magazines.models import Issue
from papers.models import Paper
from shelves.models import Acquisition, Read
from typing import Optional, TextIO


def _acquisition(args: Namespace, file: TextIO = sys.stdout):
    acquisition: Optional[Acquisition] = None
    if args.subparser == "add":
        edition = Edition.get(args.obj)
        paper = Paper.get(args.obj)
        issue = Issue.get(args.obj)

        obj = None
        if edition is None and paper is None and issue is None:
            stdout.write(_("No edition, issue or paper found."), "", file=file)
            return
        elif edition is not None and paper is None and issue is None:
            obj = edition
        elif edition is None and paper is not None and issue is None:
            obj = paper
        elif edition is None and paper is None and issue is not None:
            obj = issue

        if obj:
            acquisition, created = Acquisition.from_dict(
                {"date": args.date, "price": args.price}, obj
            )
            if created:
                stdout.write(
                    _('Successfully added acquisition with id "%(pk)d" to "%(obj)s".')
                    % {"pk": acquisition.pk, "obj": obj},
                    "=",
                    file=file,
                )
                acquisition.print(file)
            else:
                stdout.write(
                    _('The acquisition already exists with id "%(pk)d", aborting...')
                    % {"pk": acquisition.pk},
                    "",
                    file=file,
                )
        else:
            stdout.write(_("More than one paper, issue or paper found."), "", file=file)
    elif args.subparser == "delete":
        acquisition = Acquisition.get(args.acquisition)
        if acquisition:
            acquisition.delete()
            stdout.write(_("Successfully deleted acquisition."), "", file=file)
        else:
            stdout.write(_("No acquisition found."), "", file=file)
    elif args.subparser == "edit":
        acquisition = Acquisition.get(args.acquisition)
        if acquisition:
            acquisition.edit(args.edit_subparser, args.value)
            stdout.write(
                _('Successfully edited acquisition with id "%(pk)d".')
                % {"pk": acquisition.pk},
                "",
                file=file,
            )
            acquisition.print(file)
        else:
            stdout.write(_("No acquisition found."), "", file=file)
    elif args.subparser == "info":
        acquisition = Acquisition.get(args.acquisition)
        if acquisition:
            acquisition.print(file)
        else:
            stdout.write(_("No acquisition found."), "", file=file)


def _read(args: Namespace, file: TextIO = sys.stdout):
    read: Optional[Acquisition] = None
    if args.subparser == "add":
        edition = Edition.get(args.obj)
        paper = Paper.get(args.obj)
        issue = Issue.get(args.obj)

        obj = None
        if edition is None and paper is None and issue is None:
            stdout.write(_("No edition, issue or paper found."), "", file=file)
            return
        elif edition is not None and paper is None and issue is None:
            obj = edition
        elif edition is None and paper is not None and issue is None:
            obj = paper
        elif edition is None and paper is None and issue is not None:
            obj = issue

        if obj:
            read, created = Read.from_dict(
                {"started": args.started, "finished": args.finished}, obj
            )
            if created:
                stdout.write(
                    _('Successfully added read with id "%(pk)d" to "%(obj)s".')
                    % {"pk": read.pk, "obj": obj},
                    "=",
                    file=file,
                )
                read.print(file)
            else:
                stdout.write(
                    _('The read already exists with id "%(pk)d", aborting...')
                    % {"pk": read.pk},
                    "",
                    file=file,
                )
        else:
            stdout.write(_("More than one paper, issue or paper found."), "", file=file)
    elif args.subparser == "delete":
        read = Read.get(args.read)
        if read:
            read.delete()
            stdout.write(_("Successfully deleted read."), "", file=file)
        else:
            stdout.write(_("No read found."), "", file=file)
    elif args.subparser == "edit":
        read = Read.get(args.read)
        if read:
            read.edit(args.field, args.value)
            stdout.write(
                _('Successfully edited read with id "%(pk)d".') % {"pk": read.pk},
                "",
                file=file,
            )
            read.print(file)
        else:
            stdout.write(_("No read found."), "", file=file)
    elif args.subparser == "info":
        read = Read.get(args.read)
        if read:
            read.print(file)
        else:
            stdout.write(_("No read found."), "", file=file)


def add_subparser(parser: _SubParsersAction):
    """Add subparser for the shelves module."""
    # acquisition subparser
    acquisition_parser = parser.add_parser("acquisition", help=_("Manage acquisitions"))
    acquisition_parser.set_defaults(func=_acquisition)
    subparser = acquisition_parser.add_subparsers(dest="subparser")

    # acquisition add
    add_parser = subparser.add_parser("add", help=_("Add an acquisition"))
    add_parser.add_argument("obj", help=_("Edition, Paper or Issue"))
    add_parser.add_argument("--date", default=None, type=valid_date, help=_("Date"))
    add_parser.add_argument("--price", default=0, type=float, help=_("Price"))

    # acquisition delete
    delete_parser = subparser.add_parser("delete", help=_("Delete an acquisition"))
    delete_parser.add_argument("acquisition", help=_("Acquisition"))

    # acquisition edit
    edit_parser = subparser.add_parser("edit", help=_("Edit an acquisition"))
    edit_parser.add_argument("acquisition", help=_("Acquisition"))

    edit_subparser = edit_parser.add_subparsers(
        dest="edit_subparser", help=_("Which field to edit")
    )
    edit_date_parser = edit_subparser.add_parser("date")
    edit_date_parser.add_argument(
        "value", type=valid_date, help=_("New value for field")
    )

    edit_price_parser = edit_subparser.add_parser("price")
    edit_price_parser.add_argument("value", type=float, help=_("New value for field"))

    # acquisition info
    info_parser = subparser.add_parser("info", help=_("Show acquisition info"))
    info_parser.add_argument("acquisition", help=_("Acquisition"))

    # read subparser
    read_parser = parser.add_parser("read", help=_("Manage reads"))
    read_parser.set_defaults(func=_read)
    subparser = read_parser.add_subparsers(dest="subparser")

    # read add
    add_parser = subparser.add_parser("add", help=_("Add a read"))
    add_parser.add_argument("obj", help=_("Edition, Paper or Issue"))
    add_parser.add_argument(
        "--started", default=None, type=valid_date, help=_("Date started")
    )
    add_parser.add_argument(
        "--finished", default=None, type=valid_date, help=_("Date finished")
    )

    # read delete
    delete_parser = subparser.add_parser("delete", help=_("Delete a read"))
    delete_parser.add_argument("read", help=_("Read"))

    # read edit
    edit_parser = subparser.add_parser("edit", help=_("Edit a read"))
    edit_parser.add_argument("read", help=_("Read"))
    edit_parser.add_argument(
        "field", choices=["started", "finished"], help=_("Which field to edit")
    )
    edit_parser.add_argument("value", type=valid_date, help=_("New value for field"))

    # read info
    info_parser = subparser.add_parser("info", help=_("Show read info"))
    info_parser.add_argument("read", help=_("Read"))


def acquisition_subparser(parser: _SubParsersAction, arg_name: str, help_txt: str):
    """Add subparser for the acquisition model."""
    acquisition_parser = parser.add_parser("acquisition", help=_("Manage acquisition"))
    acquisition_parser.add_argument(arg_name, help=help_txt)
    subparser = acquisition_parser.add_subparsers(dest="acquisition_subparser")

    add_parser = subparser.add_parser("add", help=_("Add an acquisition"))
    add_parser.add_argument("--date", default=None, type=valid_date, help=_("Date"))
    add_parser.add_argument("--price", default=0, type=float, help=_("Price"))

    delete_parser = subparser.add_parser("delete", help=_("Delete an acquisition"))
    delete_parser.add_argument("acquisition", help=_("Acquisition"))

    edit_parser = subparser.add_parser("edit", help=_("Edit an acquisition"))
    edit_parser.add_argument("acquisition", help=_("Acquisition"))

    edit_subparser = edit_parser.add_subparsers(
        dest="edit_subparser", help=_("Which field to edit")
    )
    edit_date_parser = edit_subparser.add_parser("date")
    edit_date_parser.add_argument(
        "value", type=valid_date, help=_("New value for field")
    )

    edit_price_parser = edit_subparser.add_parser("price")
    edit_price_parser.add_argument("value", type=float, help=_("New value for field"))


def read_subparser(parser: _SubParsersAction, arg_name: str, help_txt: str):
    """Add subparser for the acquisition model."""
    read_parser = parser.add_parser("read", help=_("Manage read"))
    read_parser.add_argument(arg_name, help=help_txt)
    subparser = read_parser.add_subparsers(dest="read_subparser")

    add_parser = subparser.add_parser("add", help=_("Add a read"))
    add_parser.add_argument(
        "--started", default=None, type=valid_date, help=_("Date started")
    )
    add_parser.add_argument(
        "--finished", default=None, type=valid_date, help=_("Date finished")
    )

    delete_parser = subparser.add_parser("delete", help=_("Delete a read"))
    delete_parser.add_argument("read", help=_("Read"))

    edit_parser = subparser.add_parser("edit", help=_("Edit a read"))
    edit_parser.add_argument("read", help=_("Read"))
    edit_parser.add_argument(
        "field", choices=["started", "finished"], help=_("Which field to edit")
    )
    edit_parser.add_argument("value", type=valid_date, help=_("New value for field"))
