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


from argparse import ArgumentTypeError
from bibliothek import stdout
from books.functions import edition as fedition
from datetime import datetime, date
from django.utils.translation import ugettext_lazy as _
from magazines.functions import issue as fissue
from papers.functions import paper as fpaper
from typing import Optional


def _info(args):
    edition = fedition.get.by_term(args.obj)
    paper = fpaper.get.by_term(args.obj)
    issue = fissue.get.by_term(args.obj)

    if edition is None and paper is None and issue is None:
        return
    elif edition is not None and paper is None and issue is None:
        fedition.stdout.info(edition)
    elif edition is None and paper is not None and issue is None:
        fpaper.stdout.info(paper)
    elif edition is None and paper is None and issue is not None:
        fissue.stdout.info(issue)
    else:
        stdout.write(["More than one found."], after="=")


def add_subparser(parser):
    info_parser = parser.add_parser("info", help=_("Show info"))
    info_parser.set_defaults(func=_info)
    info_parser.add_argument("obj", help=_("Edition, Paper or Issue"))


def valid_date(s: str) -> Optional[date]:
    try:
        if s.lower() in ["", "n", "none", "null"]:
            return None
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise ArgumentTypeError(f'Not a valid date: "{s}".')
