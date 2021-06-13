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
"""Magazines Django admin."""

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import gettext_lazy as _
from files.models import File
from magazines.models import Issue, Magazine
from shelves.models import Acquisition, Read


class AcquisitionInline(GenericStackedInline):
    """Acquisition inline Django admin."""

    extra = 1
    model = Acquisition


class FileInline(GenericStackedInline):
    """File inline Django admin."""

    extra = 1
    model = File


class ReadInline(GenericStackedInline):
    """Read inline Django admin."""

    extra = 1
    model = Read


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """Issue Django admin."""

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "created_at",
                    "updated_at",
                    "magazine",
                    "issue",
                    "publishing_date",
                    "languages",
                    "cover_image",
                ]
            },
        ),
        (_("Links"), {"fields": ["links"]}),
    ]
    filter_horizontal = ("languages", "links")
    inlines = [FileInline, AcquisitionInline, ReadInline]
    list_display = ("magazine", "issue", "publishing_date", "updated_at")
    list_filter = ("magazine",)
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("magazine__name", "issue")


@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    """Magazine Django admin."""

    fieldsets = [
        (None, {"fields": ["created_at", "updated_at", "slug", "name", "feed"]}),
        (_("Links"), {"fields": ["links"]}),
    ]
    filter_horizontal = ("links",)
    list_display = ("name", "feed", "updated_at")
    readonly_fields = ("created_at", "updated_at", "slug")
    search_fields = ("name",)
