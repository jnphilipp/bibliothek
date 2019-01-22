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
from journals.models import Journal
from links.models import Link
from utils import lookahead, stdout


def create(name, links=[]):
    positions = [.33, 1.]

    journal, created = Journal.objects.get_or_create(name=name)
    if created:
        stdout.p([_('Id'), journal.id], positions=positions)
        stdout.p([_('Name'), journal.name], positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(
                Q(pk=url if url.isdigit() else None) | Q(link=url)). \
                get_or_create(defaults={'link':url})
            journal.links.add(link)
            stdout.p([_('Links') if i == 0 else '',
                      '%s: %s' % (link.id, link.link)],
                     after=None if has_next else '_', positions=positions)

        journal.save()
        msg = _('Successfully added journal "%(name)s" with id "%(id)s".')
        stdout.p([msg % {'name':journal.name, 'id':journal.id}], after='=',
                 positions=[1.])
    else:
        msg = _('The journal "%(name)s" already exists with id "%(id)s", ' +
                'aborting...')
        stdout.p([msg % {'name':journal.name, 'id':journal.id}], after='=',
                 positions=[1.])
    return journal, created


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
    msg = _('Successfully edited journal "%s" with id "%s".')
    stdout.p([msg % (journal.name, journal.id)], positions=[1.])


def info(journal):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), journal.id], positions=positions)
    stdout.p([_('Name'), journal.name], positions=positions)

    if journal.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(journal.links.all())):
            if i == 0:
                stdout.p([_('Links'),
                          '%s: %s' % (link.id, link.link)],
                         positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (link.id, link.link)],
                         positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)

    if journal.papers.count() > 0:
        for (i, paper), has_next in lookahead(enumerate(journal.papers.all())):
            if i == 0:
                stdout.p([_('Papers'), '%s: %s' % (paper.id, paper.title)],
                         positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (paper.id, paper.title)],
                         positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Papers'), ''], positions=positions)
