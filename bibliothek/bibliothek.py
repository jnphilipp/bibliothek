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

import django

django.setup()

import bibliothek.argparse
import bindings.argparse
import books.argparse
import genres.argparse
import journals.argparse
import magazines.argparse
import papers.argparse
import persons.argparse
import publishers.argparse
import series.argparse
import shelves.argparse

from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from bibliothek import (
    __app_name__,
    __author__,
    __email__,
    __github__,
    __version__,
    settings,
    stdout,
)
from bibliothek.utils import lookahead
from datetime import date, datetime
from django.utils.translation import gettext_lazy as _
from typing import TextIO


def init():
    """Init."""
    from django.core.management import execute_from_command_line

    if not settings.APP_DATA_DIR.exists():
        settings.APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    execute_from_command_line(["", "migrate", "--noinput", "-v0"])


def _import(args):
    import bindings.functions.binding as fbinding
    import books.functions.book as fbook
    import books.functions.edition as fedition
    import genres.functions as genres_functions
    import persons.functions.person as fperson
    import publishers.functions.publisher as fpublisher
    import series.functions.series as fseries
    import shelves.functions.acquisition as facquisition
    import shelves.functions.read as fread

    with open(args.path, "r", encoding="utf-8") as f:
        data = json.loads(f.read())

    if "books" in data:
        for b in data["books"]:
            authors = []
            for a in b["authors"]:
                if "first_name" in a:
                    name = f"{a['first_name']} {a['last_name']}".strip()
                else:
                    name = a["name"]
                person, c = fperson.create(name, a["links"] if "links" in a else [])
                authors.append(str(person.id))

            genres = []
            for g in b["genres"] if "genres" in b else []:
                genre, c = genres_functions.genre.create(g["name"])
                genres.append(str(genre.id))

            series, c = (
                fseries.create(
                    b["series"]["name"],
                    b["series"]["links"] if "links" in b["series"] else [],
                )
                if "series" in b
                else (None, False)
            )

            book, c = fbook.create(
                b["title"],
                authors,
                str(series.id) if series else None,
                b["volume"] if "volume" in b else 0,
                genres,
                b["links"] if "links" in b else [],
            )

            for e in b["editions"] if "editions" in b else []:
                binding, c = (
                    fbinding.create(e["binding"]["name"])
                    if "binding" in e
                    else (None, False)
                )
                publisher, c = (
                    fpublisher.create(
                        e["publisher"]["name"],
                        e["publisher"]["links"] if "links" in e["publisher"] else [],
                    )
                    if "publisher" in e
                    else (None, False)
                )

                persons = []
                for p in e["persons"] if "persons" in e else []:
                    if "first_name" in p:
                        name = f"{p['first_name']} {a['last_name']}".strip()
                    else:
                        name = a["name"]
                    person, c = fperson.create(name, a["links"] if "links" in a else [])
                    persons.append(str(person.id))

                edition, c = fedition.create(
                    book,
                    e["alternate_title"] if "alternate_title" in e else None,
                    e["isbn"] if "isbn" in e else None,
                    e["publishing_date"] if "publishing_date" in e else None,
                    e["cover"] if "cover" in e else None,
                    str(binding.id) if binding else None,
                    str(publisher.id) if publisher else None,
                    persons,
                    e["languages"] if "languages" in e else [],
                    e["links"] if "links" in e else [],
                    e["files"] if "files" in e else [],
                )

                for a in e["acquisitions"] if "acquisitions" in e else []:
                    date = a["date"] if "date" in a else None
                    price = a["price"] if "price" in a else None
                    if not date and not price:
                        continue

                    if (
                        not edition.acquisitions.filter(date=date)
                        .filter(price=price)
                        .exists()
                    ):
                        facquisition.create(edition, date, price)

                for r in e["reads"] if "reads" in e else []:
                    started = r["started"] if "started" in r else None
                    finished = r["finished"] if "finished" in r else None
                    if not started and not finished:
                        continue

                    if (
                        not edition.reads.filter(started=started)
                        .filter(finished=finished)
                        .exists()
                    ):
                        fread.create(edition, started, finished)


def _reading_list(args: Namespace, file: TextIO = sys.stdout):
    from books.models import Edition
    from magazines.models import Issue
    from papers.models import Paper
    from shelves.models import Acquisition

    reading_list = set()
    for acquisition in Acquisition.objects.all():
        if acquisition.content_object.reads.count() == 0:
            reading_list.add((acquisition.content_object, acquisition.date))
    reading_list = sorted(reading_list, key=lambda x: x[1] if x[1] else date.min)
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

    parser = ArgumentParser(prog=__app_name__, formatter_class=RawTextHelpFormatter)
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
    import_parser = subparser.add_parser("import", help=_("Import data from JSON"))
    import_parser.set_defaults(func=_import)
    import_parser.add_argument("path", help=_("JSON file"))

    # create the parser for the "reading-list" subcommand
    reading_list_parser = subparser.add_parser(
        "reading-list", help=_("Show reading-list")
    )
    reading_list_parser.set_defaults(func=_reading_list)
    reading_list_parser.add_argument(
        "--limit", type=int, help=_("Limit list to n entries")
    )

    # create the parser for the "statistics" subcommand
    statistics_parser = subparser.add_parser("statistics", help=_("Show statistics"))
    statistics_parser.set_defaults(func=_statistics)

    args = parser.parse_args()
    if args.subparser:
        args.func(args)
    else:
        parser.print_usage()
