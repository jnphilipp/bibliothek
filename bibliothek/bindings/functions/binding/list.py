# -*- coding: utf-8 -*-

from bindings.models import Binding
from django.db.models import Q
from django.utils.translation import ugettext as _
from utils import lookahead, stdout


def all():
    bindings = Binding.objects.all()
    _list([[binding.id, binding.name] for binding in bindings], [_('Id'), _('Name')], positions=[.05, 1.])
    return bindings


def by_term(term):
    bindings = Binding.objects.filter(Q(pk=term if term.isdigit() else None) | Q(name__icontains=term))
    _list([[binding.id, binding.name] for binding in bindings], [_('Id'), _('Name')], positions=[.05, 1.])
    return bindings


def _list(bindings, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for binding, has_next in lookahead(bindings):
        stdout.p(binding, positions=positions, after='_' if has_next else '=')
