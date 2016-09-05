# -*- coding: utf-8 -*-

from books.models import Book, TextFieldSingleLine
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


admin.site.register(Book, BookAdmin)
