#!/usr/bin/env python3
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

from bibliothek.argparse import valid_date
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from magazines.functions import magazine as fmagazine, issue as fissue
from shelves.argparse import acquisition_subparser, read_subparser


def _magazine(args):
    if args.subparser == 'add':
        fmagazine.create(args.name, args.feed, args.link)
    elif args.subparser == 'delete':
        magazine = fmagazine.get.by_term(args.magazine)
        if magazine:
            fmagazine.delete(magazine)
    elif args.subparser == 'edit':
        magazine = fmagazine.get.by_term(args.magazine)
        if magazine:
            fmagazine.edit(magazine, args.field, args.value)
    elif args.subparser == 'info':
        magazine = fmagazine.get.by_term(args.magazine)
        if magazine:
            fmagazine.info(magazine)
    elif args.subparser == 'issue':
        magazine = fmagazine.get.by_term(args.magazine)
        if args.issue_subparser == 'acquisition' and magazine:
            issue = fissue.get.by_term(args.issue, magazine)
            if args.acquisition_subparser == 'add' and issue:
                fissue.acquisition.add(issue, args.date, args.price)
            elif args.acquisition_subparser == 'delete' and issue:
                fissue.acquisition.delete(issue, args.acquisition)
            elif args.acquisition_subparser == 'edit' and issue:
                fissue.acquisition.edit(issue, args.acquisition,
                                        args.edit_subparser, args.value)
        elif args.issue_subparser == 'add' and magazine:
            fissue.create(magazine, args.issue, args.publishing_date,
                          args.cover, args.language, args.link, args.file)
        elif args.issue_subparser == 'edit' and magazine:
            issue = fissue.get.by_term(args.issue, magazine)
            if issue:
                fissue.edit(issue, args.edit_subparser, args.value)
        elif args.issue_subparser == 'info' and magazine:
            issue = fissue.get.by_term(args.issue, magazine)
            if issue:
                fissue.info(issue)
        elif args.issue_subparser == 'list' and magazine:
            if args.shelf:
                fissue.list.by_shelf(args.shelf, magazine)
            elif args.search:
                fissue.list.by_term(args.search, magazine)
            else:
                fissue.list.all(magazine)
        elif args.issue_subparser == 'open' and magazine:
            issue = fissue.get.by_term(args.issue, magazine)
            if issue:
                file = issue.files.get(pk=args.file)
                path = os.path.join(settings.MEDIA_ROOT, file.file.path)
                if sys.platform == 'linux':
                    os.system('xdg-open "%s"' % path)
                else:
                    os.system('open "%s"' % path)
        elif args.issue_subparser == 'read' and magazine:
            issue = fissue.get.by_term(args.issue, magazine)
            if args.read_subparser == 'add' and issue:
                fissue.read.add(issue, args.started, args.finished)
            elif args.read_subparser == 'delete' and issue:
                fissue.read.delete(issue, args.read)
            elif args.read_subparser == 'edit' and issue:
                fissue.read.edit(issue, args.read, args.field, args.value)
    elif args.subparser == 'list':
        if args.search:
            fmagazine.list.by_term(args.search)
        else:
            fmagazine.list.all()


def add_subparser(parser):
    magazine_parser = parser.add_parser('magazine', help=_('Manage magazines'))
    magazine_parser.set_defaults(func=_magazine)
    subparser = magazine_parser.add_subparsers(dest='subparser')
    issue_subparser(subparser)

    # magazine add
    add_parser = subparser.add_parser('add', help=_('Add a magazine'))
    add_parser.add_argument('name', help=_('Name'))
    add_parser.add_argument('--feed', help=_('Feed url'))
    add_parser.add_argument('--link', nargs='*', default=[], help=_('Links'))

    # magazine delete
    delete_parser = subparser.add_parser('delete', help=_('Delete a magazine'))
    delete_parser.add_argument('magazine', help=_('Magazine'))

    # magazine edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a magazine'))
    edit_parser.add_argument('magazine', help=_('Magazine'))
    edit_subparser = edit_parser.add_subparsers(dest='edit_subparser',
                                                help=_('Which field to edit'))

    edit_name_parser = edit_subparser.add_parser('name')
    edit_name_parser.add_argument('value', help=_('New value for field'))

    edit_feed_parser = edit_subparser.add_parser('feed')
    edit_feed_parser.add_argument('value', help=_('New value for field'))

    edit_link_parser = edit_subparser.add_parser('link')
    edit_link_parser.add_argument('value', help=_('New value for field'))

    # magazine info
    info_parser = subparser.add_parser('info', help=_('Show magazine info'))
    info_parser.add_argument('magazine', help=_('Magazine'))

    # magazine list
    list_parser = subparser.add_parser('list', help=_('List magazines'))
    list_parser.add_argument('--search', help=_('Filter magazines by term'))


def issue_subparser(parser):
    issue_parser = parser.add_parser('issue', help=_('Manage magazine issues'))
    issue_parser.add_argument('magazine', help=_('Magazine'))
    subparser = issue_parser.add_subparsers(dest='issue_subparser')
    acquisition_subparser(subparser, 'issue', _('Issue'))
    read_subparser(subparser, 'issue', _('Issue'))

    # magazine issue add
    add_parser = subparser.add_parser('add', help=_('Add a magazine issue'))
    add_parser.add_argument('issue', help=_('Issue'))
    add_parser.add_argument('--publishing-date', type=valid_date,
                            help=_('Publishing date'))
    add_parser.add_argument('--cover', help=_('Cover image'))
    add_parser.add_argument('--language', nargs='*', default=[],
                            help=_('Languages'))
    add_parser.add_argument('--link', nargs='*', default=[], help=_('Links'))
    add_parser.add_argument('--file', nargs='*', default=[], help=_('Files'))

    # magazine issue edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a magazine issue'))
    edit_parser.add_argument('issue', help=_('Issue'))
    edit_subparser = edit_parser.add_subparsers(dest='edit_subparser',
                                                help=_('Which field to edit'))

    edit_issue_parser = edit_subparser.add_parser('issue')
    edit_issue_parser.add_argument('value', help=_('New value for field'))

    edit_pubdate_parser = edit_subparser.add_parser('publishing-date')
    edit_pubdate_parser.add_argument('value', type=valid_date,
                                     help=_('New value for field'))

    edit_cover_parser = edit_subparser.add_parser('cover')
    edit_cover_parser.add_argument('value', help=_('New value for field'))

    edit_language_parser = edit_subparser.add_parser('language')
    edit_language_parser.add_argument('value', help=_('New value for field'))

    edit_link_parser = edit_subparser.add_parser('link')
    edit_link_parser.add_argument('value', help=_('New value for field'))

    edit_file_parser = edit_subparser.add_parser('file')
    edit_file_parser.add_argument('value', help=_('New value for field'))

    # magazine issue info
    info_parser = subparser.add_parser('info',
                                       help=_('Show magazine issue info'))
    info_parser.add_argument('issue', help=_('Issue'))

    # magazine issue list
    list_parser = subparser.add_parser('list', help=_('List issues'))
    list_parser.add_argument('--shelf', choices=['read', 'unread'],
                             help=_('Filter editions by shelf'))
    list_parser.add_argument('--search', help=_('Filter editions by term'))

    # paper open
    help_txt = _('Open a file associated with a magazine issue')
    open_parser = subparser.add_parser('open', help=help_txt)
    open_parser.add_argument('issue', nargs='?', help=_('Issue'))
    open_parser.add_argument('file', type=int, help=_('File to open'))
