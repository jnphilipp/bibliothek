# -*- coding: utf-8 -*-

from django.template import Library
register = Library()


@register.filter
def startswith(value, start):
    return value.startswith(start)


@register.filter
def endswith(value, end):
    return value.endswith(end)
