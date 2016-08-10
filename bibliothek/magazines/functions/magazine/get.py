# -*- coding: utf-8 -*-

from utils import stdout

from . import list as magazine_list


def by_term(term):
    magazines = magazine_list.by_search(term)

    if magazines.count() == 0:
        stdout.p(['No magazine found.'], after='=', positions=[1.])
        return None
    elif magazines.count() > 1:
        stdout.p(['More than one magazine found.'], after='=', positions=[1.])
        return None
    print('\n')
    return magazines[0]
