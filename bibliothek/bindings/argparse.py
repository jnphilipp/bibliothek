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
"""Bindings Django app argparse."""

import sys

from argparse import _SubParsersAction
from bibliothek import stdout
from bibliothek.utils import lookahead
from django.utils.translation import gettext_lazy as _
from bindings.models import Binding
from typing import Optional, TextIO


def _binding(args, file: TextIO = sys.stdout):
    binding: Optional[Binding] = None
    if args.subparser == "add":
        binding, created = Binding.from_dict({"name": args.name})
        if created:
            stdout.write(
                _('Successfully added binding "%(name)s" with id "%(pk)d".')
                % {"name": binding.name, "pk": binding.pk},
                "=",
                file=file,
            )
            binding.print(file)
        else:
            stdout.write(
                _('The binding "%(name)s" already exists with id "%(pk)d", aborting...')
                % {"name": binding.name, "pk": binding.pk},
                "",
                file=file,
            )
    elif args.subparser == "delete":
        binding = Binding.get(args.binding)
        if binding:
            binding.delete()
            stdout.write(
                _('Successfully deleted binding with id "%(pk)d".')
                % {"pk": binding.pk},
                "",
                file=file,
            )
        else:
            stdout.write(_("No binding found."), "", file=file)
    elif args.subparser == "edit":
        binding = Binding.get(args.binding)
        if binding:
            binding.edit(args.field, args.value)
            stdout.write(
                _('Successfully edited binding "%(name)s" with id "%(pk)d".')
                % {"name": binding.name, "pk": binding.pk},
                "",
                file=file,
            )
            binding.print(file)
        else:
            stdout.write(_("No binding found."), "", file=file)
    elif args.subparser == "info":
        binding = Binding.get(args.binding)
        if binding:
            binding.print(file)
        else:
            stdout.write(_("No binding found."), "", file=file)
    elif args.subparser == "list":
        if args.search:
            bindings = Binding.search(args.search)
        else:
            bindings = Binding.objects.all()
        stdout.write([_("Id"), _("Name")], "=", [0.05], file=file)
        for i, has_next in lookahead(bindings):
            stdout.write([i.id, i.name], "_" if has_next else "=", [0.05], file=file)


def add_subparser(parser: _SubParsersAction):
    """Add subparser for the bindings module."""
    binding_parser = parser.add_parser("binding", help=_("Manage bindings"))
    binding_parser.set_defaults(func=_binding)
    subparser = binding_parser.add_subparsers(dest="subparser")

    # binding add
    add_parser = subparser.add_parser("add", help=_("Add a new binding"))
    add_parser.add_argument("name", help=_("Name"))

    # binding delete
    delete_parser = subparser.add_parser("delete", help=_("Delete a binding"))
    delete_parser.add_argument("binding", help=_("Binding"))

    # binding edit
    edit_parser = subparser.add_parser("edit", help=_("Edit a binding"))
    edit_parser.add_argument("binding", help=_("Binding"))
    edit_parser.add_argument("field", choices=["name"], help=_("Which field to edit"))
    edit_parser.add_argument("value", help=_("New value for field"))

    # binding info
    info_parser = subparser.add_parser("info", help=_("Show binding info"))
    info_parser.add_argument("binding", help=_("Binding"))

    # binding list
    list_parser = subparser.add_parser("list", help=_("List bindings"))
    list_parser.add_argument("--search", help=_("Filter by name"))
