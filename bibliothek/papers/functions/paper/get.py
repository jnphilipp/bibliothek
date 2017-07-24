# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from utils import stdout

from . import list as paper_list


def by_term(term):
    papers = paper_list.by_term(term)

    if papers.count() == 0:
        stdout.p([_('No paper found.')], after='=', positions=[1.])
        return None
    elif papers.count() > 1:
        stdout.p([_('More than one paper found.')], after='=', positions=[1.])
        return None
    print('\n')
    return papers[0]
