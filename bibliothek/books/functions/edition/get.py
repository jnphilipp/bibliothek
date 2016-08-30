# -*- coding: utf-8 -*-

from utils import stdout

from . import list as edition_list


def by_term(book, term):
    editions = edition_list.by_term(book, term)

    if editions.count() == 0:
        stdout.p(['No edition found.'], after='=', positions=[1.])
        return None
    elif editions.count() > 1:
        stdout.p(['More than one edition found.'], after='=', positions=[1.])
        return None
    print('\n')
    return editions[0]
