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

from django.db.models import Q
from journals.models import Journal
from links.models import Link
from utils import lookahead


def create(name, links=[]):
    journal, created = Journal.objects.get_or_create(name=name)
    if created:
        for (i, l), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(Q(pk=l if l.isdigit() else None) |
                                          Q(link=l)). \
                get_or_create(defaults={'link': l})
            journal.links.add(link)
        journal.save()
    return journal, created


def delete(journal):
    journal.delete()


def edit(journal, field, value):
    assert field in ['name', 'link']

    if field == 'name':
        journal.name = value
    elif field == 'link':
        link, created = Link.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(link=value)
        ).get_or_create(defaults={'link': value})
        if journal.links.filter(pk=link.pk).exists():
            journal.links.remove(link)
        else:
            journal.links.add(link)
    journal.save()
