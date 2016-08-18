# -*- coding: utf-8 -*-

from django.contrib import admin
from django.forms import TextInput
from publishers.models import Publisher, TextFieldSingleLine


class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'updated_at')
    list_filter = ('links', )
    readonly_fields = ('slug',)
    search_fields = ('name',)

    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
    }

    fieldsets = [
        (None, {'fields': ['slug', 'name']}),
        ('links', {'fields': ['links']}),
    ]

    filter_horizontal = ('links',)


admin.site.register(Publisher, PublisherAdmin)
