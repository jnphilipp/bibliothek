# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils.translation import ugettext as _
from magazines.models import Magazine
from utils import lookahead, stdout


def all():
    magazines = Magazine.objects.all()
    _list([[magazine.id, magazine.name, magazine.issues.count()] for magazine in magazines], [_('Id'), _('Name'), _('#Issues')], positions=[.05, .8, 1.])
    return magazines


def by_term(term):
    magazines = Magazine.objects.filter(Q(pk=term if term.isdigit() else None) | Q(name__icontains=term))
    _list([[magazine.id, magazine.name, magazine.issues.count()] for magazine in magazines], [_('Id'), _('Name'), _('#Issues')], positions=[.05, .8, 1.])
    return magazines


def _list(magazines, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for magazine, has_next in lookahead(magazines):
        stdout.p(magazine, positions=positions, after='_' if has_next else '=')
