# -*- coding: utf-8 -*-

from books.models import Book, Edition, TextFieldSingleLine
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


class BookAdmin(admin.ModelAdmin):
    def list_authors(self, obj):
        return format_html_join(', ', '{} {}', ((p.first_name, p.last_name) for p in obj.authors.all()))

    list_display = ('title', 'list_authors', 'series', 'volume')
    list_filter = ('authors', 'series')
    readonly_fields = ('slug',)
    search_fields = ('title', 'authors__first_name', 'authors__last_name', 'series__name', 'volume')

    list_authors.admin_order_field = 'authors'
    list_authors.short_description = _('Authors')

    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete': 'off', 'style': 'min-width:50%;'})},
    }

    fieldsets = [
        (None, {'fields': ['slug', 'title', 'authors']}),
        ('Series', {'fields': ['series', 'volume']}),
        ('Genres', {'fields': ['genres']}),
        ('Links', {'fields': ['links']}),
    ]

    filter_horizontal = ('authors', 'genres', 'links')


class EditionAdmin(admin.ModelAdmin):
    list_display = ('book', 'isbn', 'binding', 'publisher', 'published_on')
    list_filter = ('book', 'binding', 'publisher', 'languages')
    search_fields = ('book__title', 'book__authors__first_name', 'book__authors__last_name', 'book__series__name', 'book__volume', 'isbn', 'binding__name', 'publisher__name')

    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete': 'off', 'style': 'min-width:50%;'})},
        models.TextField: {'widget': Textarea(attrs={'autocomplete': 'off', 'rows':20, 'style': 'width: 100%; resize: none;'})},
    }

    fieldsets = [
        (None, {'fields': ['book', 'alternate_title', 'isbn', 'binding', 'published_on', 'publisher', 'cover_image']}),
        ('Languages', {'fields': ['languages']}),
        ('Bibtex', {'fields': ['bibtex']}),
    ]

    inlines = [
        FileInline,
        AcquisitionInline,
        ReadInline,
    ]

    filter_horizontal = ('languages',)


admin.site.register(Book, BookAdmin)
admin.site.register(Edition, EditionAdmin)
