# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from utils import stdout

from . import list as binding_list


def by_term(term):
    bindings = binding_list.by_term(term)

    if bindings.count() == 0:
        stdout.p([_('No binding found.')], after='=', positions=[1.])
        return None
    elif bindings.count() > 1:
        stdout.p([_('More than one binding found.')], after='=', positions=[1.])
        return None
    print('\n')
    return bindings[0]
