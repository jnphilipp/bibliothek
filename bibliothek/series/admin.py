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

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from series.models import Series


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    """Series Django admin."""

    fieldsets = [
        (None, {"fields": ["created_at", "updated_at", "slug", "name"]}),
        (_("Links"), {"fields": ["links"]}),
    ]
    filter_horizontal = ("links",)
    list_display = ("name", "updated_at")
    list_filter = ("links",)
    readonly_fields = ("created_at", "updated_at", "slug")
    search_fields = ("name",)
