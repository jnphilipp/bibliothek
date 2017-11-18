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
from django.db.models import Count
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _
from journals.models import Journal, SingleLineTextField


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Journal.objects.annotate(paper_count=Count('papers'))

    def show_paper_count(self, inst):
        return inst.paper_count

    fieldsets = [
        (None, {'fields': ['slug', 'name']}),
        ('Links', {'fields': ['links']}),
    ]
    filter_horizontal = ('links',)
    formfield_overrides = {
        SingleLineTextField: {
            'widget': TextInput(attrs={'autocomplete':'off'})
        },
    }
    list_display = ('name', 'show_paper_count', 'updated_at')
    readonly_fields = ('slug',)
    search_fields = ('name',)
    show_paper_count.admin_order_field = 'paper_count'
    show_paper_count.short_description = _('Number of Papers')
