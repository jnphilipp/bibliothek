#!/usr/bin/env python3
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
"""Bibliothek."""

import json
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bibliothek.settings")

import django  # noqa: E402

django.setup()

import bibliothek.argparse  # noqa: E402
import bindings.argparse  # noqa: E402
import books.argparse  # noqa: E402
import genres.argparse  # noqa: E402
import journals.argparse  # noqa: E402
import magazines.argparse  # noqa: E402
import papers.argparse  # noqa: E402
import persons.argparse  # noqa: E402
import publishers.argparse  # noqa: E402
import series.argparse  # noqa: E402
import shelves.argparse  # noqa: E402

from argparse import (  # noqa: E402
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    FileType,
    Namespace,
    RawTextHelpFormatter,
)
from bibliothek import (  # noqa: E402
    __app_name__,
    __author__,
    __email__,
    __github__,
    __version__,
    settings,
    stdout,
)
from bibliothek.utils import lookahead  # noqa: E402
from datetime import date, datetime  # noqa: E402
from django.utils.translation import gettext_lazy as _  # noqa: E402
from typing import TextIO  # noqa: E402


class ArgFormatter(ArgumentDefaultsHelpFormatter, RawTextHelpFormatter):
    """Combination of ArgumentDefaultsHelpFormatter and RawTextHelpFormatter."""

    pass


def init():
    """Init."""
    from django.core.management import execute_from_command_line

    if not settings.APP_DATA_DIR.exists():
        settings.APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    execute_from_command_line(["", "migrate", "--noinput", "-v0"])


def _import(args):
    from books.models import Book, Edition
    from magazines.models import Issue, Magazine
    from papers.models import Paper
    from shelves.models import Acquisition, Read

    with open(args.path, "r", encoding="utf-8") as f:
        data = json.loads(f.read())

    for b in data["books"] if "books" in data else []:
        book, created = Book.from_dict(b)

        for e in b["editions"] if "editions" in b else []:
            edition, created = Edition.from_dict(e, book)

            for a in e["acquisitions"] if "acquisitions" in e else []:
                Acquisition.from_dict(a, edition)

            for r in e["reads"] if "reads" in e else []:
                Read.from_dict(a, edition)

    for m in data["magazines"] if "magazines" in data else []:
        magazine, created = Magazine.from_dict(m)

        for i in b["issues"] if "issues" in m else []:
            issue, created = Issue.from_dict(i, magazine)

            for a in i["acquisitions"] if "acquisitions" in i else []:
                Acquisition.from_dict(a, issue)

            for r in i["reads"] if "reads" in i else []:
                Read.from_dict(a, issue)

    for p in data["papers"] if "papers" in data else []:
        paper, created = Paper.from_dict(p)

        for a in p["acquisitions"] if "acquisitions" in p else []:
            Acquisition.from_dict(a, paper)

        for r in p["reads"] if "reads" in p else []:
            Read.from_dict(a, paper)


def _reading_list(args: Namespace, file: TextIO = sys.stdout):
    from books.models import Edition
    from magazines.models import Issue
    from papers.models import Paper
    from shelves.models import Acquisition

    reading_list = list()
    for acquisition in Acquisition.objects.all():
        if acquisition.content_object.reads.count() == 0:
            reading_list.append((acquisition.content_object, acquisition.date))
    reading_list = sorted(set(reading_list), key=lambda x: x[1] if x[1] else date.min)
    if args.limit:
        reading_list = reading_list[: args.limit]

    positions = [0.1, 0.15, 0.85, 1.0]
    stdout.write(
        [_("Type"), _("Id"), _("Title"), _("Acquisition")],
        "=",
        positions,
        file=file,
    )

    for item, has_next in lookahead(reading_list):
        stype = ""
        if isinstance(item[0], Paper):
            stype = "Paper"
        elif isinstance(item[0], Edition):
            stype = "Book"
        elif isinstance(item[0], Issue):
            stype = "Issue"
        stdout.write(
            [stype, item[0].id, str(item[0]), item[1] if item[1] else ""],
            "_" if has_next else "=",
            positions,
            file=file,
        )


def _statistics(args: Namespace, file: TextIO = sys.stdout):
    positions = [0.50, 0.66, 0.82, 1.0]

    from books.models import Book, Edition
    from magazines.models import Magazine, Issue
    from papers.models import Paper

    stdout.write(
        [
            _("Type"),
            _("Count"),
            _("Read"),
            _("Read %(year)d" % {"year": datetime.now().year}),
        ],
        "=",
        positions,
        file=file,
    )
    stdout.write(
        [
            _("Books"),
            Book.objects.count(),
            Book.objects.filter(editions__reads__isnull=False).count(),
            Book.objects.filter(
                editions__reads__finished__year=datetime.now().year
            ).count(),
        ],
        positions=positions,
        file=file,
    )
    stdout.write(
        [
            _("Editions"),
            Edition.objects.count(),
            Edition.objects.filter(reads__isnull=False).count(),
            Edition.objects.filter(reads__finished__year=datetime.now().year).count(),
        ],
        positions=positions,
        file=file,
    )

    stdout.write(
        [_("Magazines"), Magazine.objects.count(), 0, 0], positions=positions, file=file
    )
    stdout.write(
        [_("Issues"), Issue.objects.count(), 0, 0], positions=positions, file=file
    )
    stdout.write(
        [
            _("Papers"),
            Paper.objects.count(),
            Paper.objects.filter(reads__isnull=False).count(),
            Paper.objects.filter(reads__finished__year=datetime.now().year).count(),
        ],
        positions=positions,
        file=file,
    )


if __name__ == "__main__":
    init()

    parser = ArgumentParser(prog=__app_name__, formatter_class=ArgFormatter)
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=_(
            "%%(prog)s v%(version)s\nLizenz GPLv3+: "
            + "GNU GPL Version 3 or later "
            + "<https://gnu.org/licenses/gpl.html>.\n"
            + "Report bugs to %(github)s/issues.\n\n"
            + "Written by %(author)s <%(email)s>"
        )
        % {
            "version": __version__,
            "github": __github__,
            "author": __author__,
            "email": __email__,
        },
    )

    subparser = parser.add_subparsers(dest="subparser", metavar="COMMAND")

    # create the parser for the "info" subcommand
    bibliothek.argparse.add_subparser(subparser)

    # create the parser for the "binding" subcommand
    bindings.argparse.add_subparser(subparser)

    # create the parser for the "book" subcommand
    books.argparse.add_subparser(subparser)

    # create the parser for the "genre" subcommand
    genres.argparse.add_subparser(subparser)

    # create the parser for the "journal" subcommand
    journals.argparse.add_subparser(subparser)

    # create the parser for the "magazine" subcommand
    magazines.argparse.add_subparser(subparser)

    # create the parser for the "paper" subcommand
    papers.argparse.add_subparser(subparser)

    # create the parser for the "person" subcommand
    persons.argparse.add_subparser(subparser)

    # create the parser for the "publisher" subcommand
    publishers.argparse.add_subparser(subparser)

    # create the parser for the "series" subcommand
    series.argparse.add_subparser(subparser)

    # create the parser for the "acquisition" and "read" subcommand
    shelves.argparse.add_subparser(subparser)

    # create the parser for the "import" subcommand
    import_parser = subparser.add_parser("import", help=_("import data from JSON"))
    import_parser.set_defaults(func=_import)
    import_parser.add_argument(
        "PATH",
        type=FileType("r", encoding="utf8"),
        default=sys.stdout,
        help=_("JSON file to import from"),
    )

    # create the parser for the "reading-list" subcommand
    reading_list_parser = subparser.add_parser(
        "reading-list", help=_("show reading-list")
    )
    reading_list_parser.set_defaults(func=_reading_list)
    reading_list_parser.add_argument(
        "--limit", type=int, help=_("limit list to n entries")
    )

    # create the parser for the "statistics" subcommand
    statistics_parser = subparser.add_parser("statistics", help=_("show statistics"))
    statistics_parser.set_defaults(func=_statistics)

    args = parser.parse_args()
    if args.subparser:
        args.func(args)
    else:
        parser.print_usage()
