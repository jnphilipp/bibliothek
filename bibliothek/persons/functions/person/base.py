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
from django.utils.translation import ugettext_lazy as _
from links.models import Link
from persons.models import Person
from utils import lookahead, stdout


def create(first_name, last_name, links=[]):
    positions = [.33, 1.]

    person, created = Person.objects.get_or_create(first_name=first_name,
                                                   last_name=last_name)
    if created:
        stdout.p([_('Id'), person.id], positions=positions)
        stdout.p([_('First name'), person.first_name], positions=positions)
        stdout.p([_('Last name'), person.last_name], positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(
                Q(pk=url if url.isdigit() else None) | Q(link=url)
            ).get_or_create(defaults={'link': url})
            person.links.add(link)
            stdout.p([_('Links') if i == 0 else '', link.link],
                     after=None if has_next else '_', positions=positions)

        person.save()
        msg = _('Successfully added person "%(first_name)s %(last_name)s" ' +
                'with id "%(id)s".')
        stdout.p([msg % {'first_name': person.first_name,
                         'last_name': person.last_name, 'id': person.id}],
                 after='=', positions=[1.])
    else:
        msg = _('The person "%(first_name)s %(last_name)s" already exists ' +
                'with id "%(id)s", aborting...')
        stdout.p([msg % {'first_name': person.first_name,
                         'last_name': person.last_name, 'id': person.id}],
                 after='=', positions=[1.])
    return person, created


def edit(person, field, value):
    assert field in ['first-name', 'first_name', 'last-name', 'last_name',
                     'link']

    if field == 'first_name' or field == 'first-name':
        person.first_name = value
    elif field == 'last_name' or field == 'last-name':
        person.last_name = value
    elif field == 'link':
        link, created = Link.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(link=value)
        ).get_or_create(defaults={'link': value})
        if person.links.filter(pk=link.pk).exists():
            person.links.remove(link)
        else:
            person.links.add(link)
    person.save()
    msg = _('Successfully edited person "%(first_name)s %(last_name)s" with ' +
            'id "%(id)s".')
    stdout.p([msg % {'first_name': person.first_name,
                     'last_name': person.last_name, 'id': person.id}],
             positions=[1.])


def info(person):
    positions = [.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), person.id], positions=positions)
    stdout.p([_('First name'), person.first_name], positions=positions)
    stdout.p([_('Last name'), person.last_name if person.last_name else ''],
             positions=positions)

    if person.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(person.links.all())):
            if i == 0:
                stdout.p([_('Links'), '%s: %s' % (link.id, link.link)],
                         positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (link.id, link.link)],
                         positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)

    if person.books.count() > 0:
        for (i, book), has_next in lookahead(enumerate(person.books.all())):
            if i == 0:
                stdout.p([_('Books'), '%s: %s' % (book.id, book.title)],
                         positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (book.id, book.title)],
                         positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Books'), ''], positions=positions)

    if person.papers.count() > 0:
        for (i, paper), has_next in lookahead(enumerate(person.papers.all())):
            if i == 0:
                stdout.p([_('Papers'), '%s: %s' % (paper.id, paper.title)],
                         positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (paper.id, paper.title)],
                         positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Papers'), ''], positions=positions)
