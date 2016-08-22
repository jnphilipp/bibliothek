# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils.translation import ugettext as _
from publishers.models import Publisher
from utils import lookahead, stdout


def all():
    publishers = Publisher.objects.all()
    _list([[publisher.id, publisher.name] for publisher in publishers], [_('Id'), _('Name')], positions=[.05, 1.])
    return publishers


def by_term(term):
    publishers = Publisher.objects.filter(Q(pk=term if term.isdigit() else None) | Q(name__icontains=term))
    _list([[publisher.id, publisher.name] for publisher in publishers], [_('Id'), _('Name')], positions=[.05, 1.])
    return publishers


def _list(publishers, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for publisher, has_next in lookahead(publishers):
        stdout.p(publisher, positions=positions, after='_' if has_next else '=')
