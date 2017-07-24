# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from utils import stdout

from . import list as publisher_list


def by_term(term):
    publishers = publisher_list.by_term(term)

    if publishers.count() == 0:
        stdout.p([_('No publisher found.')], after='=', positions=[1.])
        return None
    elif publishers.count() > 1:
        stdout.p([_('More than one publisher found.')], after='=', positions=[1.])
        return None
    print('\n')
    return publishers[0]
