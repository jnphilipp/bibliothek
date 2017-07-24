# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from series.models import Series
from utils import lookahead, stdout


def all():
    series = Series.objects.all()
    _list([[series.id, series.name] for series in series], [_('Id'), _('Name')], positions=[.05, 1.])
    return series


def by_term(term):
    series = Series.objects.filter(Q(pk=term if term.isdigit() else None) | Q(name__icontains=term))
    _list([[series.id, series.name] for series in series], [_('Id'), _('Name')], positions=[.05, 1.])
    return series


def _list(series, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for series, has_next in lookahead(series):
        stdout.p(series, positions=positions, after='_' if has_next else '=')
