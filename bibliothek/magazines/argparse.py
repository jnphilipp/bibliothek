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
"""Magazines Django app argparse."""

import os
import sys

from bibliothek import stdout
from bibliothek.utils import lookahead
from argparse import _SubParsersAction, Namespace
from bibliothek.argparse import valid_date
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from links.models import Link
from magazines.models import Issue, Magazine
from shelves.argparse import acquisition_subparser, read_subparser
from shelves.models import Acquisition, Read
from typing import Optional, TextIO


def _magazine(args: Namespace, file: TextIO = sys.stdout):
    magazine: Optional[Magazine] = None
    if args.subparser == "add":
        magazine, created = Magazine.from_dict(
            {
                "name": args.name,
                "feed": Link.get_or_create(args.feed).to_dict() if args.feed else None,
                "links": [Link.get_or_create(link).to_dict() for link in args.link],
            }
        )
        if created:
            stdout.write(
                _('Successfully added magazine "%(name)s" with id "%(pk)d".')
                % {"name": magazine.name, "pk": magazine.pk},
                "=",
                file=file,
            )
        else:
            stdout.write(
                _(
                    'The magazine "%(name)s" already exists with id "%(pk)d", '
                    + "aborting..."
                )
                % {"name": magazine.name, "pk": magazine.pk},
                "",
                file=file,
            )
        magazine.print(file)
    elif args.subparser == "delete":
        magazine = Magazine.get(args.magazine)
        if magazine:
            magazine.delete()
            stdout.write(
                _('Successfully deleted magazine "%(name)s".')
                % {"name": magazine.name},
                "",
                file=file,
            )
        else:
            stdout.write(_("No magazine found."), "", file=file)
    elif args.subparser == "edit":
        magazine = Magazine.get(args.magazine)
        if magazine:
            magazine.edit(args.field, args.value)
            stdout.write(
                _('Successfully edited magazine "%(name)s" with id "%(pk)d".')
                % {"name": magazine.name, "pk": magazine.pk},
                "",
                file=file,
            )
        else:
            stdout.write(_("No magazine found."), "", file=file)
    elif args.subparser == "info":
        magazine = Magazine.get(args.magazine)
        if magazine:
            magazine.print(file)
        else:
            stdout.write(_("No magazine found."), "", file=file)
    elif args.subparser == "issue":
        magazine = Magazine.get(args.magazine)
        acquisition: Optional[Acquisition] = None
        if magazine:
            if args.issue_subparser == "acquisition" and magazine:
                issue = Issue.get(args.issue, magazine)
                if args.acquisition_subparser == "add" and issue:
                    acquisition, created = Acquisition.from_dict(
                        {"date": args.date, "price": args.price}, issue
                    )
                    if created:
                        stdout.write(
                            _('Successfully added acquisition with id "%(pk)d".')
                            % {"pk": acquisition.pk},
                            "=",
                            file=file,
                        )
                    else:
                        stdout.write(
                            _('The acquisition already exists with id "%(pk)d".')
                            % {"pk": acquisition.pk},
                            "",
                            file=file,
                        )
                    acquisition.print(file)
                elif args.acquisition_subparser == "delete" and issue:
                    acquisition = Acquisition.get(args.acquisition, issues=issue)
                    if acquisition:
                        acquisition.delete()
                        stdout.write(
                            _('Successfully deleted acquisition with id "%(pk)d".')
                            % {"pk": args.acquisition},
                            "",
                            file=file,
                        )
                    else:
                        stdout.write(_("No acquisition found."), "", file=file)
                elif args.acquisition_subparser == "edit" and issue:
                    acquisition = Acquisition.get(args.acquisition, issues=issue)
                    if acquisition:
                        acquisition.edit(args.field, args.value)
                        stdout.write(
                            _('Successfully edited acquisition with id "%(pk)d".')
                            % {"pk": acquisition.pk},
                            "=",
                            file=file,
                        )
                        acquisition.print(file)
                    else:
                        stdout.write(_("No acquisition found."), "", file=file)
                else:
                    stdout.write(_("No issue found."), "", file=file)
            elif args.issue_subparser == "add" and magazine:
                issue, created = Issue.from_dict(
                    {
                        "issue": args.issue,
                        "publishing_date": args.publishing_date,
                        "cover": args.cover,
                        "languages": args.language,
                        "links": [
                            Link.get_or_create(link).to_dict() for link in args.link
                        ],
                        "files": [{"path": file} for file in args.file],
                    },
                    magazine,
                )
                if created:
                    stdout.write(
                        _('Successfully added issue "%(issue)s" with id "%(pk)d".')
                        % {"issue": issue.issue, "pk": issue.pk},
                        "=",
                        file=file,
                    )
                else:
                    stdout.write(
                        _('The issue "%(issue)s" already exists with id "%(pk)d".')
                        % {"issue": issue.issue, "pk": issue.pk},
                        "",
                        file=file,
                    )
                issue.print(file)
            elif args.subparser == "delete" and magazine:
                issue = Issue.get(args.issue)
                if issue:
                    issue.delete()
                    stdout.write(
                        _('Successfully deleted issue with id "%(pk)s".')
                        % {"pk": issue.pk},
                        "",
                        file=file,
                    )
                else:
                    stdout.write(_("No issue found."), "", file=file)
            elif args.issue_subparser == "edit" and magazine:
                issue = Issue.get(args.issue, magazine)
                if issue:
                    issue.edit(args.edit_subparser, args.value)
                    stdout.write(
                        _('Successfully edited issue "%(issue)s" with id "%(pk)d".')
                        % {"issue": issue.issue, "pk": issue.pk},
                        "",
                        file=file,
                    )
                    issue.print(file)
                else:
                    stdout.write(_("No issue found."), "", file=file)
            elif args.issue_subparser == "info" and magazine:
                issue = Issue.get(args.issue, magazine)
                if issue:
                    issue.print(file)
                else:
                    stdout.write(_("No issue found."), "", file=file)
            elif args.issue_subparser == "list" and magazine:
                if args.search:
                    issues = Issue.search(args.search)
                elif args.shelf:
                    issues = Issue.by_shelf(args.shelf)
                else:
                    issues = Issue.objects.filter(magazine=magazine)
                stdout.write(
                    [_("Id"), _("Magazine"), _("Issue"), _("Publishing date")],
                    "=",
                    [0.05, 0.40, 0.85],
                    file=file,
                )
                for i, has_next in lookahead(issues):
                    stdout.write(
                        [i.pk, i.magazine.name, i.issue, i.publishing_date],
                        "_" if has_next else "=",
                        [0.05, 0.40, 0.85],
                        file=file,
                    )
            elif args.issue_subparser == "open" and magazine:
                issue = Issue.get(args.issue, magazine)
                if issue:
                    issue_file = issue.files.get(pk=args.file)
                    path = settings.MEDIA_ROOT / issue_file.file.path
                    if sys.platform == "linux":
                        os.system(f'xdg-open "{path}"')
                    else:
                        os.system(f'open "{path}"')
                else:
                    stdout.write(_("No issue found."), "", file=file)
            elif args.issue_subparser == "read" and magazine:
                issue = Issue.get(args.issue, magazine)
                read: Optional[Read] = None
                if args.read_subparser == "add" and issue:
                    read, created = Read.from_dict(
                        {"started": args.started, "finished": args.finished}, issue
                    )
                    if created:
                        stdout.write(
                            _('Successfully added read with id "%(pk)s".')
                            % {"pk": read.pk},
                            "=",
                            file=file,
                        )
                    else:
                        stdout.write(
                            _('The read already exists with id "%(pk)s".')
                            % {"pk": read.pk},
                            "",
                            file=file,
                        )
                    read.print(file)
                elif args.read_subparser == "delete" and issue:
                    read = Read.get(args.read, issues=issue)
                    if read:
                        read.delete()
                        stdout.write(
                            _('Successfully deleted read with id "%(pk)s".')
                            % {"pk": read.pk},
                            "",
                            file=file,
                        )
                    else:
                        stdout.write(_("No read found."), "", file=file)
                elif args.read_subparser == "edit" and issue:
                    read = Read.get(args.read, issues=issue)
                    if read:
                        read.edit(args.field, args.value)
                        stdout.write(
                            _('Successfully edited read with id "%(pk)s".')
                            % {"pk": read.pk},
                            "=",
                            file=file,
                        )
                        read.info(file)
                    else:
                        stdout.write(_("No read found."), "", file=file)
                else:
                    stdout.write(_("No issue found."), "", file=file)
        else:
            stdout.write(_("No magazine found."), "", file=file)
    elif args.subparser == "list":
        if args.search:
            magazines = Magazine.search(args.search)
        else:
            magazines = Magazine.objects.all()

        stdout.write(
            [_("Id"), _("Name"), _("Number of issues")],
            "=",
            [0.05, 0.8],
            file=file,
        )
        for i, has_next in lookahead(magazines):
            stdout.write(
                [i.pk, i.name, i.issues.count()],
                "_" if has_next else "=",
                [0.05, 0.8],
                file=file,
            )


def add_subparser(parser: _SubParsersAction):
    """Add subparser for the Magazine model."""
    magazine_parser = parser.add_parser("magazine", help=_("Manage magazines"))
    magazine_parser.set_defaults(func=_magazine)
    subparser = magazine_parser.add_subparsers(dest="subparser")
    issue_subparser(subparser)

    # magazine add
    add_parser = subparser.add_parser("add", help=_("Add a magazine"))
    add_parser.add_argument("name", help=_("Name"))
    add_parser.add_argument("--feed", help=_("Feed url"))
    add_parser.add_argument("--link", nargs="*", default=[], help=_("Links"))

    # magazine delete
    delete_parser = subparser.add_parser("delete", help=_("Delete a magazine"))
    delete_parser.add_argument("magazine", help=_("Magazine"))

    # magazine edit
    edit_parser = subparser.add_parser("edit", help=_("Edit a magazine"))
    edit_parser.add_argument("magazine", help=_("Magazine"))
    edit_subparser = edit_parser.add_subparsers(
        dest="edit_subparser", help=_("Which field to edit")
    )

    edit_name_parser = edit_subparser.add_parser("name")
    edit_name_parser.add_argument("value", help=_("New value for field"))

    edit_feed_parser = edit_subparser.add_parser("feed")
    edit_feed_parser.add_argument("value", help=_("New value for field"))

    edit_link_parser = edit_subparser.add_parser("link")
    edit_link_parser.add_argument("value", help=_("New value for field"))

    # magazine info
    info_parser = subparser.add_parser("info", help=_("Show magazine info"))
    info_parser.add_argument("magazine", help=_("Magazine"))

    # magazine list
    list_parser = subparser.add_parser("list", help=_("List magazines"))
    list_parser.add_argument("--search", help=_("Filter magazines by term"))


def issue_subparser(parser: _SubParsersAction):
    """Add subparser for the Issue model."""
    issue_parser = parser.add_parser("issue", help=_("Manage magazine issues"))
    issue_parser.add_argument("magazine", help=_("Magazine"))
    subparser = issue_parser.add_subparsers(dest="issue_subparser")
    acquisition_subparser(subparser, "issue", _("Issue"))
    read_subparser(subparser, "issue", _("Issue"))

    # magazine issue add
    add_parser = subparser.add_parser("add", help=_("Add a magazine issue"))
    add_parser.add_argument("issue", help=_("Issue"))
    add_parser.add_argument(
        "--publishing-date", type=valid_date, help=_("Publishing date")
    )
    add_parser.add_argument("--cover", help=_("Cover image"))
    add_parser.add_argument("--language", nargs="*", default=[], help=_("Languages"))
    add_parser.add_argument("--link", nargs="*", default=[], help=_("Links"))
    add_parser.add_argument("--file", nargs="*", default=[], help=_("Files"))

    # magazine issue delete
    delete_parser = subparser.add_parser("delete", help=_("Delete magazine issue"))
    delete_parser.add_argument("issue", help=_("Issue"))

    # magazine issue edit
    edit_parser = subparser.add_parser("edit", help=_("Edit a magazine issue"))
    edit_parser.add_argument("issue", help=_("Issue"))
    edit_subparser = edit_parser.add_subparsers(
        dest="edit_subparser", help=_("Which field to edit")
    )

    edit_issue_parser = edit_subparser.add_parser("issue")
    edit_issue_parser.add_argument("value", help=_("New value for field"))

    edit_pubdate_parser = edit_subparser.add_parser("publishing-date")
    edit_pubdate_parser.add_argument(
        "value", type=valid_date, help=_("New value for field")
    )

    edit_cover_parser = edit_subparser.add_parser("cover")
    edit_cover_parser.add_argument("value", help=_("New value for field"))

    edit_language_parser = edit_subparser.add_parser("language")
    edit_language_parser.add_argument("value", help=_("New value for field"))

    edit_link_parser = edit_subparser.add_parser("link")
    edit_link_parser.add_argument("value", help=_("New value for field"))

    edit_file_parser = edit_subparser.add_parser("file")
    edit_file_parser.add_argument("value", help=_("New value for field"))

    # magazine issue info
    info_parser = subparser.add_parser("info", help=_("Show magazine issue info"))
    info_parser.add_argument("issue", help=_("Issue"))

    # magazine issue list
    list_parser = subparser.add_parser("list", help=_("List issues"))
    list_parser.add_argument(
        "--shelf", choices=["read", "unread"], help=_("Filter editions by shelf")
    )
    list_parser.add_argument("--search", help=_("Filter editions by term"))

    # magazine issue open
    help_txt = _("Open a file associated with a magazine issue")
    open_parser = subparser.add_parser("open", help=help_txt)
    open_parser.add_argument("issue", nargs="?", help=_("Issue"))
    open_parser.add_argument("file", type=int, help=_("File to open"))
