# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils.translation import ugettext as _
from journals.models import Journal
from utils import lookahead, stdout


def all():
    journals = Journal.objects.all()
    _list([[journal.id, journal.name, journal.papers.count()] for journal in journals], [_('Id'), _('Name'), _('#Papers')], positions=[.5, .9, 1.])
    return journals


def by_term(term):
    journals = Journal.objects.filter(Q(pk=term if term.isdigit() else None) | Q(name__icontains=term))
    _list([[journal.id, journal.name, journal.papers.count()] for journal in journals], [_('Id'), _('Name'), _('#Papers')], positions=[.5, .9, 1.])
    return journals


def _list(journals, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for journal, has_next in lookahead(journals):
        stdout.p(journal, positions=positions, after='_' if has_next else '=')
