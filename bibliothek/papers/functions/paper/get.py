# -*- coding: utf-8 -*-

from . import list as paper_list


def by_term(term):
    papers = paper_list.by_search(term)

    if papers.count() == 0:
        stdout.p(['No paper found.'], after='=', positions=[1.])
        return None
    elif papers.count() > 1:
        stdout.p(['More than one paper found.'], after='=', positions=[1.])
        return None
    print('=' * 100)
    print('\n\n')
    return papers[0]
