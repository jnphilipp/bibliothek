# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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
from persons.models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Person.objects.annotate(book_count=Count('books'),
                                       paper_count=Count('papers'))

    def show_book_count(self, inst):
        return inst.book_count

    def show_paper_count(self, inst):
        return inst.paper_count

    fieldsets = [
        (None, {'fields': ['slug', 'name']}),
        (_('Links'), {'fields': ['links']}),
    ]
    filter_horizontal = ('links',)
    list_display = ('name', 'show_paper_count', 'show_book_count')
    readonly_fields = ('slug',)
    search_fields = ('name',)
    show_book_count.admin_order_field = 'book_count'
    show_book_count.short_description = _('Number of Books')
    show_paper_count.admin_order_field = 'paper_count'
    show_paper_count.short_description = _('Number of Papers')
