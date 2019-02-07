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
from magazines.functions import magazine as fmagazine, issue as fissue
from shelves.argparse import acquisition_subparser, read_subparser
from shelves.functions import acquisition as facquisition, read as fread


def _magazine(args):
    if args.subparser == 'add':
        magazine, created = fmagazine.create(args.name, args.feed, args.link)
        if created:
            msg = _(f'Successfully added magazine "{magazine.name}" with id ' +
                    f'"{magazine.id}".')
            utils.stdout.p([msg], '=')
            fmagazine.utils.info(magazine)
        else:
            msg = _(f'The magazine "{magazine.name}" already exists with id ' +
                    f'"{magazine.id}", aborting...')
            utils.stdout.p([msg], '')
    elif args.subparser == 'delete':
        magazine = fmagazine.get.by_term(args.magazine)
        if magazine:
            fmagazine.delete(magazine)
            msg = _(f'Successfully deleted magazine "{magazine.name}" with ' +
                    f'id "{magazine.id}".')
            utils.stdout.p([msg], '')
        else:
            utils.stdout.p([_('No magazine found.')], '')
    elif args.subparser == 'edit':
        magazine = fmagazine.get.by_term(args.magazine)
        if magazine:
            fmagazine.edit(magazine, args.field, args.value)
            msg = _(f'Successfully edited magazine "{magazine.name}" with id' +
                    f' "{magazine.id}".')
            utils.stdout.p([msg], '')
        else:
            utils.stdout.p([_('No magazine found.')], '')
    elif args.subparser == 'info':
        magazine = fmagazine.get.by_term(args.magazine)
        if magazine:
            fmagazine.stdout.info(magazine)
        else:
            utils.stdout.p([_('No magazine found.')], '')
    elif args.subparser == 'issue':
        magazine = fmagazine.get.by_term(args.magazine)
        if magazine:
            if args.issue_subparser == 'acquisition' and magazine:
                issue = fissue.get.by_term(args.issue, magazine)
                if args.acquisition_subparser == 'add' and issue:
                    acquisition = facquisition.create(issue, args.date,
                                                      args.price)
                    msg = _('Successfully added acquisition with id ' +
                            f'"{acquisition.id}".')
                    utils.stdout.p([msg], '=')
                    facquisition.stdout.info(acquisition)
                elif args.acquisition_subparser == 'delete' and issue:
                    acquisition = facquisition.get.by_pk(args.acquisition,
                                                         issue=issue)
                    if acquisition:
                        facquisition.delete(acquisition)
                        msg = _('Successfully deleted acquisition with id ' +
                                f'"{acquisition.id}".')
                        utils.stdout.p([msg], '')
                    else:
                        utils.stdout.p(['No acquisition found.'], '')
                elif args.acquisition_subparser == 'edit' and issue:
                    acquisition = facquisition.get.by_pk(args.acquisition,
                                                         issue=issue)
                    if acquisition:
                        facquisition.edit(acquisition, args.field, args.value)
                        msg = _('Successfully edited acquisition with id ' +
                                f'"{acquisition.id}".')
                        utils.stdout.p([msg], '=')
                        facquisition.stdout.info(acquisition)
                    else:
                        utils.stdout.p(['No acquisition found.'], '')
            elif args.issue_subparser == 'add' and magazine:
                issue, created = fissue.create(magazine, args.issue,
                                               args.publishing_date,
                                               args.cover, args.language,
                                               args.link, args.file)
                if issue:
                    msg = _(f'Successfully added issue "{magazine.name} ' +
                            f'{issue.issue}" with id "{issue.id}".')
                    utils.stdout.p([msg], '=')
                    fissue.stdout.info(issue)
                else:
                    msg = _(f'The issue "{magazine.name} {issue.issue}' +
                            f'" already exists with id "{issue.id}", ' +
                            'aborting...')
                    utils.stdout.p([msg], '')
            elif args.issue_subparser == 'edit' and magazine:
                issue = fissue.get.by_term(args.issue, magazine)
                if issue:
                    fissue.edit(issue, args.edit_subparser, args.value)
                    msg = _(f'Successfully edited issue "{magazine.name} ' +
                            f'{issue.issue}" with id "{issue.id}".')
                    utils.stdout.p([msg], '=')
                    fissue.stdout.info(issue)
                else:
                    utils.stdout.p(['No issue found.'], '')
            elif args.issue_subparser == 'info' and magazine:
                issue = fissue.get.by_term(args.issue, magazine)
                if issue:
                    fissue.stdout.info(issue)
                else:
                    utils.stdout.p(['No issue found.'], '')
            elif args.issue_subparser == 'list' and magazine:
                if args.shelf:
                    issues = fissue.list.by_shelf(args.shelf, magazine)
                elif args.search:
                    issues = fissue.list.by_term(args.search, magazine)
                else:
                    issues = fissue.list.all(magazine)
                fissue.stdout.list(issues)
            elif args.issue_subparser == 'open' and magazine:
                issue = fissue.get.by_term(args.issue, magazine)
                if issue:
                    file = issue.files.get(pk=args.file)
                    path = os.path.join(settings.MEDIA_ROOT, file.file.path)
                    if sys.platform == 'linux':
                        os.system(f'xdg-open "{path}"')
                    else:
                        os.system(f'open "{path}"')
                else:
                    utils.stdout.p(['No issue found.'], '')
            elif args.edition_subparser == 'read' and magazine:
                issue = fissue.get.by_term(args.issue, magazine)
                if args.read_subparser == 'add' and issue:
                    read = fread.create(issue, args.started, args.finished)
                    msg = _(f'Successfully added read with id "{read.id}".')
                    utils.stdout.p([msg], '=')
                    fread.stdout.info(read)
                elif args.read_subparser == 'delete' and issue:
                    read = fread.get.by_pk(args.read, issue=issue)
                    if read:
                        fread.delete(read)
                        msg = _('Successfully deleted read with id ' +
                                f'"{read.id}".')
                        utils.stdout.p([msg], '')
                    else:
                        utils.stdout.p(['No read found.'], '')
                elif args.read_subparser == 'edit' and issue:
                    read = fread.get.by_pk(args.read, issue=issue)
                    if read:
                        fread.edit(read, args.field, args.value)
                        msg = _('Successfully edited read with id ' +
                                f'"{read.id}".')
                        utils.stdout.p([msg], '=')
                        fread.stdout.info(read)
                    else:
                        utils.stdout.p(['No read found.'], '')
                else:
                    utils.stdout.p(['No issue found.'], '')
        else:
            utils.stdout.p([_('No magazine found.')], '')
    elif args.subparser == 'list':
        if args.search:
            magazines = fmagazine.list.by_term(args.search)
        else:
            magazines = fmagazine.list.all()
        fmagazine.stdout.list(magazines)


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
