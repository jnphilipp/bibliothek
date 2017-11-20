# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.db.models import Count
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _
from files.models import File
from magazines.models import Issue, Magazine, SingleLineTextField
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


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['magazine', 'issue', 'published_on', 'languages',
                           'cover_image']}),
        (_('Links'), {'fields': ['links']}),
    ]
    filter_horizontal = ('languages', 'links')
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={'autocomplete': 'off'})
        },
    }
    inlines = [FileInline, AcquisitionInline, ReadInline]
    list_display = ('magazine', 'issue', 'published_on', 'updated_at')
    list_filter = ('magazine',)
    search_fields = ('magazine__name', 'issue')


@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Magazine.objects.annotate(magazine_count=Count('issues'))

    def show_magazine_count(self, inst):
        return inst.magazine_count

    fieldsets = [
        (None, {'fields': ['slug', 'name', 'feed']}),
        (_('Links'), {'fields': ['links']}),
    ]
    filter_horizontal = ('links',)
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={'autocomplete': 'off'})
        },
    }
    list_display = ('name', 'feed', 'show_magazine_count', 'updated_at')
    readonly_fields = ('slug',)
    search_fields = ('name',)
    show_magazine_count.admin_order_field = 'magazine_count'
    show_magazine_count.short_description = _('Number of Issues')
