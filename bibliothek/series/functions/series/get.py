# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from utils import stdout

from . import list as series_list


def by_term(term):
    series = series_list.by_term(term)

    if series.count() == 0:
        stdout.p([_('No series found.')], after='=', positions=[1.])
        return None
    elif series.count() > 1:
        stdout.p([_('More than one series found.')], after='=', positions=[1.])
        return None
    print('\n')
    return series[0]
