# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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
from django.forms import TextInput
from series.models import Series, SingleLineTextField


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['slug', 'name']}),
        ('links', {'fields': ['links']}),
    ]
    filter_horizontal = ('links',)
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={'autocomplete':'off'})
        },
    }
    list_display = ('name', 'updated_at')
    list_filter = ('links', )
    readonly_fields = ('slug',)
    search_fields = ('name',)

