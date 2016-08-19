# -*- coding: utf-8 -*-

from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext as _
from persons.models import Person
from utils import lookahead, stdout


def all():
    persons = Person.objects.all()
    _list([[person.first_name, person.last_name] for person in persons], [_('First name'), _('Last name')], positions=[.55, 1.])
    return persons


def by_term(term):
    persons = Person.objects.annotate(name=Concat('first_name', Value(' '), 'last_name')).filter(name__icontains=term)
    _list([[person.first_name, person.last_name] for person in persons], [_('First name'), _('Last name')], positions=[.55, 1.])
    return persons


def _list(persons, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for person, has_next in lookahead(persons):
        stdout.p(person, positions=positions, after='_' if has_next else '=')
