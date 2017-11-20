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

from django.conf import settings
from django.template import Library
from django.utils.html import format_html
from django.utils.safestring import mark_safe
register = Library()

@register.filter
def currency_symbol(price):
    if settings.CURRENCY_SYMBOL:
        return '%.02f %s' % (price, settings.CURRENCY_SYMBOL)
    else:
        return '%.02f' % price

@register.simple_tag
def read_status(reads):
    if reads.filter(finished__isnull=False).exists():
        return mark_safe('<span class="glyphicon glyphicon-ok">')
    elif reads.filter(started__isnull=False).exists():
        return mark_safe('<span class="glyphicon glyphicon-time">')
    else:
        return mark_safe('<span class="glyphicon glyphicon-remove">')
