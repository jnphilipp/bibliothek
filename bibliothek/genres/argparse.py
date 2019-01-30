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

from genres.functions import genre as fgenre
from django.utils.translation import ugettext_lazy as _


def _genre(args):
    if args.subparser == 'add':
        genre, created = fgenre.create(args.name)
        if created:
            msg = _(f'Successfully added genre "{genre.name}" with id ' +
                    f'"{genre.id}".')
            utils.stdout.p([msg], '=')
            fgenre.stdout.info(genre)
        else:
            msg = _(f'The genre "{genre.name}" already exists with id ' +
                    f'"{genre.id}", aborting...')
            utils.stdout.p([msg], '')
    elif args.subparser == 'delete':
        genre = fgenre.get.by_term(args.genre)
        if genre:
            fgenre.delete(genre)
            msg = _(f'Successfully deleted genre with id "{genre.id}".')
            utils.stdout.p([msg], '')
        else:
            utils.stdout.p([_('No genre found.')], '')
    elif args.subparser == 'edit':
        genre = fgenre.get.by_term(args.genre)
        if genre:
            fgenre.edit(genre, args.field, args.value)
            msg = _(f'Successfully edited genre "{genre.name}" with id ' +
                    f'"{genre.id}".')
            utils.stdout.p([msg], '')
            fgenre.stdout.info(genre)
        else:
            utils.stdout.p([_('No genre found.')], '')
    elif args.subparser == 'info':
        genre = fgenre.get.by_term(args.genre)
        if genre:
            fgenre.stdout.info(genre)
        else:
            utils.stdout.p([_('No genre found.')], '')
    elif args.subparser == 'list':
        if args.search:
            genres = fgenre.list.by_term(args.search)
        else:
            genres = fgenre.list.all()
        fgenre.stdout.list(genres)


def add_subparser(parser):
    genre_parser = parser.add_parser('genre', help=_('Manage genres'))
    genre_parser.set_defaults(func=_genre)
    subparser = genre_parser.add_subparsers(dest='subparser')

    # genre add
    add_parser = subparser.add_parser('add', help=_('Add a genre'))
    add_parser.add_argument('name', help=_('Name'))

    # genre delete
    delete_parser = subparser.add_parser('delete', help=_('Delete a genre'))
    delete_parser.add_argument('genre', help=_('Genre'))

    # genre edit
    edit_parser = subparser.add_parser('edit', help=_('Edit a genre'))
    edit_parser.add_argument('genre', help=_('Genre'))
    edit_parser.add_argument('field', choices=['name'],
                             help=_('Which field to edit'))
    edit_parser.add_argument('value', help=_('New value for field'))

    # genre info
    info_parser = subparser.add_parser('info', help=_('Show genre info'))
    info_parser.add_argument('genre', help=_('Genre'))

    # genre list
    list_parser = subparser.add_parser('list', help=_('List genres'))
    list_parser.add_argument('--search', help=_('Filter genres by term'))
