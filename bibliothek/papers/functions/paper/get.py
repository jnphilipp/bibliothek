# -*- coding: utf-8 -*-

from utils import stdout

from . import list as paper_list


def by_term(term):
    papers = paper_list.by_term(term)

    if papers.count() == 0:
        stdout.p(['No paper found.'], after='=', positions=[1.])
        return None
    elif papers.count() > 1:
        stdout.p(['More than one paper found.'], after='=', positions=[1.])
        return None
    print('\n')
    return papers[0]
