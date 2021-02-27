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
"""Shelves argparse."""

import datetime
import os
import sys
import utils

from bibliothek import stdout
from bibliothek.utils import lookahead
from argparse import _SubParsersAction, Namespace
from bibliothek.argparse import valid_date
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from papers.models import Paper
from shelves.models import Acquisition, Read
from shelves.argparse import acquisition_subparser, read_subparser
from typing import Optional, TextIO


def _paper(args: Namespace, file: TextIO = sys.stdout):
    paper: Optional[Paper] = None
    if args.subparser == "acquisition":
        paper = Paper.get(args.paper)
        acquisition: Optional[Acquisition] = None
        if args.acquisition_subparser == "add" and paper:
            acquisition, created = Acquisition.from_dict(
                {"date": args.date, "price": args.price}, paper
            )
            if created:
                stdout.write(
                    _(f'Successfully added acquisition with id "{acquisition.pk}".'),
                    "=",
                    file=file,
                )
            else:
                stdout.write(
                    _(f'The acquisition already exists with id "{acquisition.pk}".'),
                    "",
                    file=file,
                )
            acquisition.print(file)
        elif args.acquisition_subparser == "delete" and paper:
            acquisition = Acquisition.get(args.acquisition, papers=paper)
            if acquisition:
                acquisition.delete(acquisition)
                stdout.write(
                    _(f'Successfully deleted acquisition with id "{acquisition.pk}".'),
                    "",
                    file=file,
                )
            else:
                stdout.write(_("No acquisition found."), "", file=file)
        elif args.acquisition_subparser == "edit" and paper:
            acquisition = Acquisition.get(args.acquisition, papers=paper)
            if acquisition:
                acquisition.edit(args.field, args.value)
                stdout.write(
                    _(f'Successfully edited acquisition with id "{acquisition.pk}".'),
                    "=",
                    file=file,
                )
                acquisition.print(file)
            else:
                utils.stdout.p(["No acquisition found."], "")
        else:
            stdout.write(_("No paper found."), "", file=file)
    elif args.subparser == "add":
        paper, created = Paper.from_dict(
            {
                "title": args.title,
                "authors": [{"name": author} for author in args.author],
                "publishing_date": args.publishing_date,
                "journal": {"name": args.journal},
                "volume": args.volume,
                "languages": [{"name": language} for language in args.language],
                "links": [{"name": link} for link in args.link],
                "files": [{"path": file} for file in args.file],
            }
        )
        if created:
            stdout.write(
                _(f'Successfully added paper "{paper.name}" with id "{paper.pk}".'),
                "=",
                file=file,
            )
        else:
            stdout.write(
                _(f'The paper "{paper.name}" already exists with id "{paper.pk}".'),
                "",
                file=file,
            )
        paper.print(file)
    elif args.subparser == "delete":
        paper = Paper.get(args.paper)
        if paper:
            paper.delete()
            stdout.write(
                _(f'Successfully deleted paper with id "{paper.pk}".'),
                "",
                file=file,
            )
        else:
            stdout.write(_("No paper found."), "", file=file)
    elif args.subparser == "edit":
        paper = Paper.get(args.paper)
        if paper:
            paper.edit(args.edit_subparser, args.value)
            stdout.write(
                _(
                    f'Successfully edited paper "{paper.title}" with id '
                    + f'"{paper.pk}".'
                ),
                "",
                file=file,
            )
            paper.print(file)
        else:
            stdout.write(_("No series found."), "", file=file)
    elif args.subparser == "info":
        paper = Paper.get(args.paper)
        if paper:
            paper.print(file)
        else:
            stdout.write(_("No paper found."), "", file=file)
    elif args.subparser == "list":
        if args.search:
            papers = Paper.search(args.search)
        elif args.shelf:
            papers = Paper.by_shelf(args.shelf)
        else:
            papers = Paper.objects.all()
        stdout.write(
            [_("Id"), _("Name"), _("Journal"), _("Volume")],
            "=",
            [0.05, 0.7, 0.85],
            file=file,
        )
        for i, has_next in lookahead(papers):
            stdout.write(
                [i.id, i.name, i.journal.name, i.volume],
                "_" if has_next else "=",
                [0.05, 0.7, 0.85],
                file=file,
            )
    elif args.subparser == "open":
        paper = Paper.get(args.paper)
        if paper:
            paper_file = paper.files.get(pk=args.file)
            path = os.path.join(settings.MEDIA_ROOT, paper_file.file.path)
            if sys.platform == "linux":
                os.system(f'xdg-open "{path}"')
            else:
                os.system(f'open "{path}"')
        else:
            stdout.write(_("No paper found."), "", file=file)
    elif args.subparser == "parse":
        for paper, created in Paper.from_bibfile(args.bibfile, args.file):
            if created:
                stdout.write(
                    _(
                        f'Successfully added paper "{paper.title}" with id '
                        + f'"{paper.pk}".'
                    ),
                    file=file,
                )
                if args.acquisition:
                    acquisition, created = Acquisition.from_dict(
                        {"date": datetime.date.today()}, paper
                    )
                    if created:
                        stdout.write(
                            _(
                                "Successfully added acquisition with id "
                                + f'"{acquisition.pk}".'
                            ),
                            "=",
                            file=file,
                        )
                    else:
                        stdout.write(
                            _(
                                "The acquisition already exists with id "
                                + f'"{acquisition.pk}".'
                            ),
                            "=",
                            file=file,
                        )
            else:
                stdout.write(
                    _(
                        f'The paper "{paper.title}" already exists with id '
                        + f'"{paper.pk}".'
                    ),
                    "=",
                    file=file,
                )
            paper.print(file)
    elif args.subparser == "read":
        paper = Paper.get(args.paper)
        read: Optional[Read] = None
        if args.read_subparser == "add" and paper:
            read, created = Read.from_dict(
                {"started": args.started, "finished": args.finished}, paper
            )
            if created:
                stdout.write(
                    _(f'Successfully added read with id "{read.pk}".'), "=", file=file
                )
            else:
                stdout.write(
                    _(f'The read already exists with id "{paper.pk}".'),
                    "",
                    file=file,
                )
            read.print(file)
        elif args.read_subparser == "delete" and paper:
            read = Read.get(args.read, papers=paper)
            if read:
                read.delete()
                stdout.write(
                    _(f'Successfully deleted read with id "{read.pk}".'), "", file=file
                )
            else:
                stdout.write(_("No read found."), "", file=file)
        elif args.read_subparser == "edit" and paper:
            read = Read.get(args.read, papers=paper)
            if read:
                read.edit(args.field, args.value)
                stdout.write(
                    _(f'Successfully edited read with id "{read.pk}".'), "=", file=file
                )
                read.info(file)
            else:
                stdout.write(_("No read found."), "", file=file)
        else:
            stdout.write(_("No paper found."), "", file=file)


def add_subparser(parser: _SubParsersAction):
    """Add subparser for the papers module."""
    paper_parser = parser.add_parser("paper", help=_("Manage papers"))
    paper_parser.set_defaults(func=_paper)
    subparser = paper_parser.add_subparsers(dest="subparser")
    acquisition_subparser(subparser, "paper", _("Paper"))
    read_subparser(subparser, "paper", _("Paper"))

    # paper add
    add_parser = subparser.add_parser("add", help=_("Add a paper"))
    add_parser.add_argument("title", help=_("Title"))
    add_parser.add_argument("--author", nargs="*", default=[], help=_("Authors"))
    add_parser.add_argument(
        "--publishing-date", type=valid_date, help=_("Publishing date")
    )
    add_parser.add_argument("--journal", help=_("journal"))
    add_parser.add_argument("--volume", help=_("Volume"))
    add_parser.add_argument("--language", nargs="*", default=[], help=_("Languages"))
    add_parser.add_argument("--link", nargs="*", default=[], help=_("Links"))
    add_parser.add_argument("--file", nargs="*", default=[], help=_("Additional files"))

    # paper edit
    edit_parser = subparser.add_parser("edit", help=_("Edit a paper"))
    edit_parser.add_argument("paper", help=_("Paper"))
    edit_subparser = edit_parser.add_subparsers(
        dest="edit_subparser", help=_("Which field to edit")
    )

    edit_title_parser = edit_subparser.add_parser("title")
    edit_title_parser.add_argument("value", help=_("New value for field"))

    edit_author_parser = edit_subparser.add_parser("author")
    edit_author_parser.add_argument("value", help=_("New value for field"))

    edit_pubdate_parser = edit_subparser.add_parser("publishing-date")
    edit_pubdate_parser.add_argument(
        "value", type=valid_date, help=_("New value for field")
    )

    edit_journal_parser = edit_subparser.add_parser("journal")
    edit_journal_parser.add_argument("value", help=_("New value for field"))

    edit_volume_parser = edit_subparser.add_parser("volume")
    edit_volume_parser.add_argument("value", help=_("New value for field"))

    edit_language_parser = edit_subparser.add_parser("language")
    edit_language_parser.add_argument("value", help=_("New value for field"))

    edit_link_parser = edit_subparser.add_parser("link")
    edit_link_parser.add_argument("value", help=_("New value for field"))

    edit_file_parser = edit_subparser.add_parser("file")
    edit_file_parser.add_argument("value", help=_("New value for field"))

    # paper list
    list_parser = subparser.add_parser("list", help=_("List papers"))
    list_parser.add_argument(
        "--shelf",
        choices=["read", "unread"],
        nargs="?",
        help=_("Filter editions by shelf"),
    )
    list_parser.add_argument("--search", help=_("Filter editions by term"))

    # paper info
    info_parser = subparser.add_parser("info", help=_("Show paper info"))
    info_parser.add_argument("paper", help=_("Paper"))

    # paper open
    open_parser = subparser.add_parser(
        "open", help=_("Open a file associated with a paper")
    )
    open_parser.add_argument("paper", nargs="?", help=_("Paper"))
    open_parser.add_argument("file", type=int, help=_("File to open"))

    # paper parse
    parse_parser = subparser.add_parser("parse", help=_("Add papers from bibfile."))
    parse_parser.add_argument("bibfile", help=_("Bibfile"))
    parse_parser.add_argument(
        "-f", "--file", nargs="*", default=[], help=_("Additional files")
    )
    parse_parser.add_argument(
        "-a",
        "--acquisition",
        action="store_true",
        help=_("Add acquisition for parsed papers."),
    )
