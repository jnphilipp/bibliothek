# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db.models import Count
from django.forms import TextInput
from links.models import Link


class LinkAdmin(admin.ModelAdmin):
    list_display = ('link', 'updated_at')
    search_fields = ('link',)


    fieldsets = [
        (None, {'fields': ['link']}),
    ]


admin.site.register(Link, LinkAdmin)
