#!/usr/bin/env python3
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# -*- coding: utf-8 -*-
# Copyright (C) 2016-2022 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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
"""Bibliothek GNOME search provider."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bibliothek.settings")

import django  # noqa: E402

django.setup()

import dbus  # noqa: E402
import dbus.glib  # noqa: E402
import dbus.service  # noqa: E402
import os  # noqa: E402
import sys  # noqa: E402

from books.models import Edition  # noqa: E402
from django.db.models import Q  # noqa: E402
from gi.repository import GLib  # noqa: E402
from magazines.models import Issue  # noqa: E402
from papers.models import Paper  # noqa: E402

search_bus_name = "org.gnome.Shell.SearchProvider2"
sbn = dict(dbus_interface=search_bus_name)


class BibliothekSearchService(dbus.service.Object):
    """Bibliothek search provider."""

    bus_name = "org.gnome.bibliothek.SearchProvider"
    _object_path = "/" + bus_name.replace(".", "/")
    default_cover = os.path.abspath("./bibliothek/static/images/default_cover.jpg")

    def __init__(self):
        """Init."""
        self.session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(self.bus_name, bus=self.session_bus)
        dbus.service.Object.__init__(self, bus_name, self._object_path)

    @dbus.service.method(in_signature="sasu", **sbn)
    def ActivateResult(self, id, terms, timestamp):  # noqa: N802
        """Activate result item."""
        obj = self._get_obj(id)
        if obj is not None:
            if obj.files.count() > 1:
                files = obj.files.filter(
                    Q(file__iendswith=".epub")
                    | Q(file__iendswith=".pdf")
                    | Q(file__iendswith=".mobi")
                )
                if files.count() == 0:
                    path = obj.files.first().file.path
                else:
                    path = files.first().file.path
            else:
                path = obj.files.first().file.path

            if sys.platform == "linux":
                os.system('xdg-open "%s"' % path)
            else:
                os.system('open "%s"' % path)

    @dbus.service.method(in_signature="as", out_signature="as", **sbn)
    def GetInitialResultSet(self, terms):  # noqa: N802
        """Get initial result set."""
        return self._get_result_set(terms)

    @dbus.service.method(in_signature="as", out_signature="aa{sv}", **sbn)
    def GetResultMetas(self, ids):  # noqa: N802
        """Get result metas."""
        metas = []
        for id in ids:
            obj = self._get_obj(id)
            if obj is None:
                continue
            elif id.startswith("edition"):
                name = f"{obj.book}"
                gicon = obj.cover_image.path if obj.cover_image else self.default_cover
            elif id.startswith("paper"):
                name = f"{obj}"
                gicon = self.default_cover
            elif id.startswith("issue"):
                name = f"{obj}"
                gicon = obj.cover_image.path if obj.cover_image else self.default_cover

            metas.append({"id": id, "name": name, "gicon": gicon})
        return metas

    @dbus.service.method(in_signature="asas", out_signature="as", **sbn)
    def GetSubsearchResultSet(self, previous_results, new_terms):  # noqa: N802
        """Get subsearch result set."""
        return self._get_result_set(new_terms)

    @dbus.service.method(in_signature="asu", terms="as", timestamp="u", **sbn)
    def LaunchSearch(self, terms, timestamp):  # noqa: N802
        """Launch search."""
        pass

    def _get_obj(self, id):
        if id.startswith("edition"):
            return Edition.get(id[8:])
        elif id.startswith("paper"):
            return Paper.get(id[6:])
        elif id.startswith("issue"):
            return Issue.get(id[6:])
        else:
            return None

    def _get_result_set(self, terms):
        term = " ".join(terms)
        editions = Edition.search(term, has_file=True)
        results = [f"edition-{e.pk}" for e in editions]

        papers = Paper.search(term, has_file=True)
        results += [f"paper-{p.pk}" for p in papers]

        issues = Issue.search(term, has_file=True)
        results += [f"issue-{i.pk}" for i in issues]
        return results

    def notify(self, message, body="", error=False):
        """Send notification."""
        try:
            self.session_bus.get_object(
                "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
            ).Notify(
                "bibliothek",
                0,
                "bibliothek",
                message,
                body,
                "",
                {"transient": False if error else True},
                0 if error else 3000,
                dbus_interface="org.freedesktop.Notifications",
            )
        except dbus.DBusException as e:
            print(f"Got error {e} while trying to display message {message}.")


if __name__ == "__main__":
    BibliothekSearchService()
    GLib.MainLoop().run()
