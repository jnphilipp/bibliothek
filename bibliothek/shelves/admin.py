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
from django.forms import TextInput

from .models import Acquisition, Read


@admin.register(Acquisition)
class AcquisitionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['date', 'price', 'content_type', 'object_id']}),
    ]
    list_display = ('id', 'content_object', 'date', 'price', 'updated_at')
    list_filter = ('content_type', 'object_id')
    search_fields = ('id',)


@admin.register(Read)
class ReadAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['started', 'finished', 'content_type',
                           'object_id']}),
    ]
    list_display = ('id', 'content_object', 'started', 'finished',
                    'updated_at')
    list_filter = ('content_type', 'object_id')
    search_fields = ('id',)
