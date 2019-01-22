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

from books.models import Book, Edition
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.db import models
from django.forms import Textarea, TextInput
from django.utils.html import format_html_join
from django.utils.translation import ugettext_lazy as _
from files.models import File
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


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    def list_authors(self, obj):
        return format_html_join(', ', '{} {}',
                                ((p.first_name,
                                  p.last_name) for p in obj.authors.all()))

    fieldsets = [
        (None, {'fields': ['slug', 'title', 'authors']}),
        (_('Series'), {'fields': ['series', 'volume']}),
        (_('Genres'), {'fields': ['genres']}),
        (_('Links'), {'fields': ['links']}),
    ]
    filter_horizontal = ('authors', 'genres', 'links')
    list_authors.admin_order_field = 'authors'
    list_authors.short_description = _('Authors')
    list_display = ('title', 'list_authors', 'series', 'volume')
    list_filter = ('authors', 'series')
    readonly_fields = ('slug',)
    search_fields = ('title', 'authors__first_name', 'authors__last_name',
                     'series__name', 'volume')


@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['book', 'alternate_title', 'isbn', 'binding',
                           'publishing_date', 'publisher', 'cover_image']}),
        (_('Languages'), {'fields': ['languages']}),
        (_('Persons'), {'fields': ['persons']}),
        (_('Bibtex'), {'fields': ['bibtex']}),
    ]
    filter_horizontal = ('languages', 'persons')
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={
                'autocomplete': 'off',
                'rows': 20,
                'style': 'width: 100%; resize: none;'
            })
        },
    }
    inlines = [FileInline, AcquisitionInline, ReadInline]
    list_display = ('book', 'isbn', 'binding', 'publisher', 'publishing_date')
    list_filter = ('book', 'binding', 'publisher', 'languages')
    search_fields = ('book__title', 'book__authors__first_name',
                     'book__authors__last_name', 'book__series__name',
                     'book__volume', 'isbn', 'binding__name',
                     'publisher__name')
