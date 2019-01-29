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
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliothek.settings')

import django
django.setup()

import dbus
import dbus.glib
import dbus.service
import os
import sys

from books.functions import edition as fedition
from django.db.models import Q
from gi.repository import GLib
from magazines.functions import issue as fissue
from papers.functions import paper as fpaper

search_bus_name = 'org.gnome.Shell.SearchProvider2'
sbn = dict(dbus_interface=search_bus_name)


class BibliothekSearchService(dbus.service.Object):
    bus_name = 'org.gnome.bibliothek.SearchProvider'
    _object_path = '/' + bus_name.replace('.', '/')
    default_cover = os.path.abspath('./bibliothek/static/images/' +
                                    'default_cover.jpg')

    def __init__(self):
        self.session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(self.bus_name, bus=self.session_bus)
        dbus.service.Object.__init__(self, bus_name, self._object_path)

    @dbus.service.method(in_signature='sasu', **sbn)
    def ActivateResult(self, id, terms, timestamp):
        obj = self.get_obj(id)
        if obj is not None:
            if obj.files.count() > 1:
                files = obj.files.filter(Q(name__iendswith='.epub') |
                                         Q(name__iendswith='.pdf') |
                                         Q(name__iendswith='.mobi'))
                if files.count() == 0:
                    path = obj.files.first().file.path
                else:
                    path = files.first().file.path
            else:
                path = obj.files.first().file.path

            if sys.platform == 'linux':
                os.system('xdg-open "%s"' % path)
            else:
                os.system('open "%s"' % path)

    @dbus.service.method(in_signature='as', out_signature='as', **sbn)
    def GetInitialResultSet(self, terms):
        return self.get_result_set(terms)

    @dbus.service.method(in_signature='as', out_signature='aa{sv}', **sbn)
    def GetResultMetas(self, ids):
        metas = []
        for id in ids:
            obj = self.get_obj(id)
            if obj is None:
                continue
            elif id.startswith('edition'):
                name = f'{obj.book}'
                gicon = obj.cover_image.path if obj.cover_image \
                    else self.default_cover
            elif id.startswith('paper'):
                name = f'{obj}'
                gicon = self.default_cover
            elif id.startswith('issue'):
                name = f'{obj}'
                gicon = obj.cover_image.path if obj.cover_image \
                    else self.default_cover

            metas.append({
                'id': id,
                'name': name,
                'gicon': gicon
            })
        return metas

    @dbus.service.method(in_signature='asas', out_signature='as', **sbn)
    def GetSubsearchResultSet(self, previous_results, new_terms):
        return self.get_result_set(new_terms)

    @dbus.service.method(in_signature='asu', terms='as', timestamp='u', **sbn)
    def LaunchSearch(self, terms, timestamp):
        pass

    def get_obj(self, id):
        if id.startswith('edition'):
            return fedition.get.by_pk(id[8:])
        elif id.startswith('paper'):
            return fpaper.get.by_pk(id[6:])
        elif id.startswith('issue'):
            return fissue.get.by_pk(id[6:])
        else:
            return None

    def get_result_set(self, terms):
        term = ' '.join(terms)
        editions = fedition.list.by_term(term, has_file=True)
        results = [f'edition-{e.pk}' for e in editions]

        papers = fpaper.list.by_term(term, has_file=True)
        results += [f'paper-{e.pk}' for e in papers]

        issues = fissue.list.by_term(term, has_file=True)
        results += [f'issue-{e.pk}' for e in issues]
        return results

    def notify(self, message, body='', error=False):
        try:
            self.session_bus.get_object('org.freedesktop.Notifications',
                                        '/org/freedesktop/Notifications'). \
                Notify('bibliothek', 0, 'bibliothek', message, body, '',
                       {'transient': False if error else True},
                       0 if error else 3000,
                       dbus_interface='org.freedesktop.Notifications')
        except dbus.DBusException as e:
            print(f'Got error {e} while trying to display message {message}.')


def main():
    search_service = BibliothekSearchService()
    GLib.MainLoop().run()


if __name__ == '__main__':
    main()
