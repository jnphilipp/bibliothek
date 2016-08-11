# -*- coding: utf-8 -*-

from utils import stdout

from . import list as issue_list


def by_term(magazine, term):
    issues = issue_list.by_term(magazine, term)

    if issues.count() == 0:
        stdout.p(['No issue found.'], after='=', positions=[1.])
        return None
    elif issues.count() > 1:
        stdout.p(['More than one issue found.'], after='=', positions=[1.])
        return None
    print('\n')
    return issues[0]
