# -*- coding: utf-8 -*-

from utils import stdout

from . import list as journal_list


def by_term(term):
    journals = journal_list.by_term(term)

    if journals.count() == 0:
        stdout.p(['No journal found.'], after='=', positions=[1.])
        return None
    elif journals.count() > 1:
        stdout.p(['More than one journal found.'], after='=', positions=[1.])
        return None
    print('\n')
    return journals[0]
