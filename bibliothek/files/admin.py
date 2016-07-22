# -*- coding: utf-8 -*-

from django.contrib import admin
from files.models import File


class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'updated_at')
    search_fields = ('file',)

    fieldsets = [
        (None, {'fields': ['file', 'content_type', 'object_id']}),
    ]


admin.site.register(File, FileAdmin)
