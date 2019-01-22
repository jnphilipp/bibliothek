# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
#
# This file is part of bibliothek.
#
# bibliothek is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# bibliothek is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with bibliothek.  If not, see <http://www.gnu.org/licenses/>.

from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _
from persons.models import Person
from utils import lookahead, stdout


def all():
    persons = Person.objects.all()
    _list([[person.id, person.first_name,
            person.last_name if person.last_name else '', person.books.count(),
            person.papers.count()] for person in persons],
          [_('Id'), _('First name'), _('Last name'), _('#Books'),
           _('#Papers')], positions=[.05, .425, .8, .9, 1.])
    return persons


def by_term(term):
    persons = Person.objects.annotate(
        name=Concat('first_name', Value(' '), 'last_name')
    ).filter(Q(pk=term if term.isdigit() else None) | Q(name__icontains=term))
    _list([[person.id, person.first_name,
            person.last_name if person.last_name else '', person.books.count(),
            person.papers.count()] for person in persons],
          [_('Id'), _('First name'), _('Last name'), _('#Books'),
           _('#Papers')], positions=[.05, .425, .8, .9, 1.])
    return persons


def _list(persons, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for person, has_next in lookahead(persons):
        stdout.p(person, positions=positions, after='_' if has_next else '=')
