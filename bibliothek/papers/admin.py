# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django.forms import Textarea, TextInput
from django.utils.html import format_html_join
from papers.models import Paper, TextFieldSingleLine


class PaperAdmin(admin.ModelAdmin):
    def list_authors(self, obj):
        return format_html_join(', ', '{} {}', ((p.first_name, p.last_name) for p in obj.authors.all()))

    list_display = ('title', 'list_authors', 'journal', 'volume', 'updated_at')
    list_filter = ('authors', 'journal')
    readonly_fields = ('slug',)
    search_fields = ('title', 'journal__name', 'volume')


    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
        models.TextField: {'widget': Textarea(attrs={'autocomplete':'off', 'rows':20, 'style':'width: 100%; resize: none;'})},
    }

    fieldsets = [
        (None, {'fields': ['slug', 'title', 'authors', 'languages']}),
        ('Journal', {'fields': ['journal', 'volume', 'published_on']}),
        ('Bibtex', {'fields': ['bibtex']}),
        ('Links', {'fields': ['links']}),
    ]

    filter_horizontal = ('authors', 'languages', 'links')


admin.site.register(Paper, PaperAdmin)
