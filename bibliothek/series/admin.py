# -*- coding: utf-8 -*-

from django.contrib import admin
from django.forms import TextInput
from series.models import Series, TextFieldSingleLine


class SeriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'updated_at')
    readonly_fields = ('slug',)
    search_fields = ('name',)

    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
    }

    fieldsets = [
        (None, {'fields': ['slug', 'name']}),
    ]


admin.site.register(Series, SeriesAdmin)
