# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from utils import stdout

from . import list as person_list


def by_term(term):
    persons = person_list.by_term(term)

    if persons.count() == 0:
        stdout.p([_('No person found.')], after='=', positions=[1.])
        return None
    elif persons.count() > 1:
        stdout.p([_('More than one person found.')], after='=', positions=[1.])
        return None
    print('\n')
    return persons[0]
