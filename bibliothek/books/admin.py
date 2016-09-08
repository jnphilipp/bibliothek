# -*- coding: utf-8 -*-

from books.models import Book, Edition, TextFieldSingleLine
from django.contrib import admin
from django.db import models
from django.forms import Textarea, TextInput
from django.utils.translation import ugettext as _


class BookAdmin(admin.ModelAdmin):
    def get_authors(self, inst):
        return ', '.join([str(a) for a in inst.authors.all()])

    list_display = ('title', 'get_authors', 'series', 'volume')
    list_filter = ('authors', 'series')
    readonly_fields = ('slug',)
    search_fields = ('title', 'authors__first_name', 'authors__last_name', 'series__name', 'volume')

    get_authors.admin_order_field = 'authors'
    get_authors.short_description = _('Authors')

    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off', 'style':'min-width:50%;'})},
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
    list_filter = ('book', 'binding', 'publisher')
    search_fields = ('book__title', 'book__authors__first_name', 'book__authors__last_name', 'book__series__name', 'book__volume', 'isbn', 'binding__name', 'publisher__name')

    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off', 'style':'min-width:50%;'})},
        models.TextField: {'widget': Textarea(attrs={'autocomplete':'off', 'rows':20, 'style':'width: 100%; resize: none;'})},
    }

    fieldsets = [
        (None, {'fields': ['book', 'alternate_title', 'isbn', 'binding', 'published_on', 'publisher', 'cover_image']}),
        ('Languages', {'fields': ['languages']}),
        ('Bibtex', {'fields': ['bibtex']}),
    ]

    filter_horizontal = ('languages',)


admin.site.register(Book, BookAdmin)
admin.site.register(Edition, EditionAdmin)
