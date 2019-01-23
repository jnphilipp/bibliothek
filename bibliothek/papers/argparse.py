# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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

import os
import sys
import utils

from bibliothek.argparse import valid_date
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from papers.functions import paper as fpaper
from shelves.argparse import acquisition_subparser, read_subparser
from shelves.functions import acquisition as facquisition, read as fread


def _paper(args):
    if args.subparser == 'acquisition':
        paper = fpaper.get.by_term(args.paper)
        if args.acquisition_subparser == 'add' and paper:
            acquisition = facquisition.create(paper, args.date, args.price)
            facquisition.stdout.info(acquisition)
        elif args.acquisition_subparser == 'delete' and paper:
            acquisition = facquisition.get.by_pk(args.acquisition, paper=paper)
            if acquisition:
                facquisition.delete(acquisition)
            else:
                utils.stdout.p(['No acquisition found.'], '')
        elif args.acquisition_subparser == 'edit' and paper:
            acquisition = facquisition.get.by_pk(args.acquisition, paper=paper)
            if acquisition:
                facquisition.edit(acquisition, args.field, args.value)
                facquisition.stdout.info(acquisition)
            else:
                utils.stdout.p(['No acquisition found.'], '')
        else:
            utils.stdout.p(['No paper found.'], '')
    elif args.subparser == 'add':
        paper, created = fpaper.create(args.title, args.author,
                                       args.publishing_date, args.journal,
                                       args.volume, args.language, args.link)
        if created:
            msg = _(f'Successfully added paper "{paper.title}" with id ' +
                    f'"{paper.id}".')
            utils.stdout.p([msg], '=')
            fpaper.stdout.info(paper)
        else:
            msg = _(f'The paper "{paper.title}" already exists with id ' +
                    f'"{paper.id}", aborting...')
            utils.stdout.p([msg], '')
    elif args.subparser == 'edit':
        paper = fpaper.get.by_term(args.paper)
        if paper:
            fpaper.edit(paper, args.edit_subparser, args.value)
            msg = _(f'Successfully edited paper "{paper.title}" with id ' +
                    f'"{paper.id}".')
            utils.stdout.p([msg])
        else:
            utils.stdout.p(['No paper found.'], '')
    elif args.subparser == 'list':
        if args.shelf:
            papers = fpaper.list.by_shelf(args.shelf)
        elif args.search:
            papers = fpaper.list.by_term(args.search)
        else:
            papers = fpaper.list.all()
            fpaper.stdout.list(papers)
    elif args.subparser == 'info':
        paper = fpaper.get.by_term(args.paper)
        if paper:
            fpaper.stdout.info(paper)
        else:
            utils.stdout.p(['No paper found.'], '')
    elif args.subparser == 'open':
        paper = fpaper.get.by_term(args.paper)
        if paper:
            file = paper.files.get(pk=args.file)
            path = os.path.join(settings.MEDIA_ROOT, file.file.path)
            if sys.platform == 'linux':
                os.system('xdg-open "%s"' % path)
            else:
                os.system('open "%s"' % path)
        else:
            utils.stdout.p(['No paper found.'], '')
    elif args.subparser == 'parse':
        papers = fpaper.parse.from_bibtex(args.bibtex, args.file)
        for paper, created, acquisition in papers:
            if created:
                msg = _(f'Successfully added paper "{paper.title}" with id ' +
                        f'"{paper.id}".')
                utils.stdout.p([msg])
                msg = _(f'Successfully added acquisition on '
                        f'"{acquisition.date}" with id "{acquisition.id}".')
                utils.stdout.p([msg], '=')
                fpaper.stdout.info(paper)
            else:
                msg = _(f'The paper "{paper.title}" already exists with id' +
                        f' "{paper.id}", aborting...')
                utils.stdout.p([msg], '=')
    elif args.subparser == 'read':
        paper = fpaper.get.by_term(args.paper)
        if args.read_subparser == 'add' and paper:
            read = fread.create(paper, args.started, args.finished)
            fread.stdout.info(read)
        elif args.read_subparser == 'delete' and paper:
            read = fread.get.by_pk(args.read, paper=paper)
            if read:
                fread.delete(read)
            else:
                utils.stdout.p(['No read found.'], '')
        elif args.read_subparser == 'edit' and paper:
            read = fread.get.by_pk(args.read, paper=paper)
            if read:
                fread.edit(read, args.field, args.value)
                fread.stdout.info(read)
            else:
                utils.stdout.p(['No read found.'], '')
        else:
            utils.stdout.p(['No paper found.'], '')


def add_subparser(parser):
    paper_parser = parser.add_parser('paper', help=_('Manage papers'))
    paper_parser.set_defaults(func=_paper)
    subparser = paper_parser.add_subparsers(dest='subparser')
    acquisition_subparser(subparser, 'paper', _('Paper'))
    read_subparser(subparser, 'paper', _('Paper'))

    # paper add
    add_parser = subparser.add_parser('add', help=_('Add a paper'))
    add_parser.add_argument('title', help=_('Title'))
    add_parser.add_argument('--author', nargs='*', default=[],
                            help=_('Authors'))
    add_parser.add_argument('--publishing-date', type=valid_date,
                            help=_('Publishing date'))
    add_parser.add_argument('--journal', help=_('journal'))
    add_parser.add_argument('--volume', help=_('Volume'))
    add_parser.add_argument('--language', nargs='*', default=[],
                            help=_('Languages'))
    add_parser.add_argument('--link', nargs='*', default=[], help=_('Links'))

    # paper edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a paper'))
    edit_parser.add_argument('paper', help=_('Paper'))
    edit_subparser = edit_parser.add_subparsers(dest='edit_subparser',
                                                help=_('Which field to edit'))

    edit_title_parser = edit_subparser.add_parser('title')
    edit_title_parser.add_argument('value', help=_('New value for field'))

    edit_author_parser = edit_subparser.add_parser('author')
    edit_author_parser.add_argument('value', help=_('New value for field'))

    edit_pubdate_parser = edit_subparser.add_parser('publishing-date')
    edit_pubdate_parser.add_argument('value', type=valid_date,
                                     help=_('New value for field'))

    edit_journal_parser = edit_subparser.add_parser('journal')
    edit_journal_parser.add_argument('value', help=_('New value for field'))

    edit_volume_parser = edit_subparser.add_parser('volume')
    edit_volume_parser.add_argument('value', help=_('New value for field'))

    edit_language_parser = edit_subparser.add_parser('language')
    edit_language_parser.add_argument('value', help=_('New value for field'))

    edit_link_parser = edit_subparser.add_parser('link')
    edit_link_parser.add_argument('value', help=_('New value for field'))

    edit_file_parser = edit_subparser.add_parser('file')
    edit_file_parser.add_argument('value', help=_('New value for field'))

    # paper list
    list_parser = subparser.add_parser('list', help=_('List papers'))
    list_parser.add_argument('--shelf', choices=['read', 'unread'], nargs='?',
                             help=_('Filter editions by shelf'))
    list_parser.add_argument('--search', help=_('Filter editions by term'))

    # paper info
    info_parser = subparser.add_parser('info', help=_('Show paper info'))
    info_parser.add_argument('paper', help=_('Paper'))

    # paper open
    help_txt = _('Open a file associated with a paper')
    open_parser = subparser.add_parser('open', help=help_txt)
    open_parser.add_argument('paper', nargs='?', help=_('Paper'))
    open_parser.add_argument('file', type=int, help=_('File to open'))

    # paper parse
    parse_parser = subparser.add_parser('parse',
                                        help=_('Add papers from bibtex file'))
    parse_parser.add_argument('bibtex', help=_('Bibtex file'))
    parse_parser.add_argument('-f', '--file', nargs='*', default=[],
                              help=_('Additional files'))
