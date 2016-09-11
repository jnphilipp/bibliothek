# -*- coding: utf-8 -*-

from django.conf import settings
from django.template import Library
from django.utils.html import format_html
from django.utils.safestring import mark_safe
register = Library()

@register.filter
def currency_symbol(price):
    return '%s %s' % (price, settings.CURRENCY_SYMBOL) if settings.CURRENCY_SYMBOL else price

@register.simple_tag
def read_status(reads):
    if reads.filter(finished__isnull=False).exists():
        return mark_safe('<span class="glyphicon glyphicon-ok">')
    elif reads.filter(started__isnull=False).exists():
        return mark_safe('<span class="glyphicon glyphicon-time">')
    else:
        return mark_safe('<span class="glyphicon glyphicon-remove">')
