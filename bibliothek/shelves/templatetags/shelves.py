# -*- coding: utf-8 -*-

from django.template import Library
from django.utils.html import format_html
from django.utils.safestring import mark_safe
register = Library()


@register.simple_tag
def read_status(reads):
    if reads.filter(finished__isnull=False).exists():
        return mark_safe('<span class="glyphicon glyphicon-ok">')
    elif reads.filter(started__isnull=False).exists():
        return mark_safe('<span class="glyphicon glyphicon-time">')
    else:
        return mark_safe('<span class="glyphicon glyphicon-remove">')
