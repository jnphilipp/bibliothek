# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from utils import stdout

from . import list as genre_list


def by_term(term):
    genres = genre_list.by_term(term)

    if genres.count() == 0:
        stdout.p([_('No genre found.')], after='=', positions=[1.])
        return None
    elif genres.count() > 1:
        stdout.p([_('More than one genre found.')], after='=', positions=[1.])
        return None
    print('\n')
    return genres[0]
