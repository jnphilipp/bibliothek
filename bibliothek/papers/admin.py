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
from django.contrib.contenttypes.admin import GenericStackedInline
from django.db import models
from django.forms import Textarea, TextInput
from django.utils.html import format_html_join
from django.utils.translation import ugettext_lazy as _
from files.models import File
from papers.models import Paper, SingleLineTextField
from shelves.models import Acquisition, Read


class AcquisitionInline(GenericStackedInline):
    extra = 1
    model = Acquisition


class FileInline(GenericStackedInline):
    extra = 1
    model = File


class ReadInline(GenericStackedInline):
    extra = 1
    model = Read


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    def list_authors(self, obj):
        return format_html_join(
            ', '
            '{} {}',
            ((p.first_name, p.last_name) for p in obj.authors.all())
        )

    fieldsets = [
        (None, {'fields': ['slug', 'title', 'authors', 'languages']}),
        (_('Journal'), {'fields': ['journal', 'volume', 'publishing_date']}),
        (_('Bibtex'), {'fields': ['bibtex']}),
        (_('Links'), {'fields': ['links']}),
    ]
    filter_horizontal = ('authors', 'languages', 'links')
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={'autocomplete': 'off'})
        },
        models.TextField: {
            'widget': Textarea(attrs={
                'autocomplete': 'off',
                'rows': 20,
                'style': 'width: 100%; resize: none;'
            })
        },
    }
    inlines = [FileInline, AcquisitionInline, ReadInline]
    list_display = ('title', 'list_authors', 'journal', 'volume', 'updated_at')
    list_filter = ('authors', 'journal')
    readonly_fields = ('slug',)
    search_fields = ('title', 'journal__name', 'volume')
