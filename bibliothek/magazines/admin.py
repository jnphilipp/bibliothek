# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db.models import Count
from django.forms import TextInput
from magazines.models import Issue, Magazine, TextFieldSingleLine


class IssueAdmin(admin.ModelAdmin):
    list_display = ('magazine', 'issue', 'published_on', 'updated_at')
    list_filter = ('magazine',)
    readonly_fields = ('slug',)
    search_fields = ('magazine__name', 'issue')

    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
    }

    fieldsets = [
        (None, {'fields': ['slug', 'magazine', 'issue', 'published_on', 'languages', 'cover_image']}),
        ('Links', {'fields': ['links']}),
    ]

    filter_horizontal = ('languages', 'links')


class MagazineAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Magazine.objects.annotate(magazine_count=Count('issues'))


    def show_magazine_count(self, inst):
        return inst.magazine_count

    list_display = ('name', 'feed', 'show_magazine_count', 'updated_at')
    readonly_fields = ('slug',)
    search_fields = ('name',)
    show_magazine_count.admin_order_field = 'magazine_count'
    show_magazine_count.short_description = 'Number of Issues'

    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
    }

    fieldsets = [
        (None, {'fields': ['slug', 'name', 'feed']}),
        ('Links', {'fields': ['links']}),
    ]

    filter_horizontal = ('links',)


admin.site.register(Issue, IssueAdmin)
admin.site.register(Magazine, MagazineAdmin)
