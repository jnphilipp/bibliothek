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
"""Links Django app admin."""

from django.contrib import admin
from files.models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    """File admin."""

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "created_at",
                    "updated_at",
                    "file",
                    "content_type",
                    "object_id",
                ]
            },
        ),
    ]
    list_display = ("id", "file", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("file",)
