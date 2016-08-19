# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils.translation import ugettext as _
from series.models import Series
from utils import lookahead, stdout


def all():
    series = Series.objects.all()
    _list([[series.name] for series in series], [_('Name')], positions=[.55, 1.])
    return series


def by_term(term):
    series = Series.objects.filter(name__icontains=term)
    _list([[series.name] for series in series], [_('Name')], positions=[.55, 1.])
    return series


def _list(series, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for series, has_next in lookahead(series):
        stdout.p(series, positions=positions, after='_' if has_next else '=')
