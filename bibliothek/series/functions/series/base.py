# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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
from series.models import Series
from utils import lookahead, stdout


def create(name, links=[]):
    positions = [.33, 1.]

    series, created = Series.objects.get_or_create(name=name)
    if created:
        stdout.p([_('Id'), series.id], positions=positions)
        stdout.p([_('Name'), series.name], positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(
                Q(pk=url if url.isdigit() else None) | Q(link=url)
            ).get_or_create(defaults={'link':url})
            series.links.add(link)
            stdout.p([_('Links') if i == 0 else '', link.link],
                     after=None if has_next else '_', positions=positions)

        series.save()
        msg = _('Successfully added series "%(name)s" with id "%(id)s".')
        stdout.p([msg % {'name':series.name, 'id':series.id}], after='=',
                 positions=[1.])
    else:
        msg = _('The series "%(name)s" already exists with id "%(id)s", ' +
                'aborting...')
        stdout.p([msg % {'name':series.name, 'id':series.id}], after='=',
                 positions=[1.])
    return series, created


def edit(series, field, value):
    assert field in ['name', '+link', '-link']

    if field == 'name':
        series.name = value
    elif field == '+link':
        link, created = Link.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(link=value)
        ).get_or_create(defaults={'link':value})
        series.links.add(link)
    elif field == '-link':
        try:
            link = Link.objects.get(
                Q(pk=value if value.isdigit() else None) | Q(link=value)#
            )
            series.links.remove(link)
        except Link.DoesNotExist:
            stdout.p([_('Link "%(name)s" not found.') % {'name':value}],
                     positions=[1.])
    series.save()
    msg = _('Successfully edited series "%(name)s" with id "%(id)s".')
    stdout.p([msg % {'name':series.name, 'id':series.id}], positions=[1.])


def info(series):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), series.id], positions=positions)
    stdout.p([_('Name'), series.name], positions=positions)

    if series.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(series.links.all())):
            stdout.p([_('Links') if i == 0 else '',
                      '%s: %s' % (link.id, link.link)], positions=positions,
                     after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)

    if series.books.count() > 0:
        books = series.books.all().order_by('volume')
        for (i, book), has_next in lookahead(enumerate(books)):
            stdout.p([_('Books') if i == 0 else '',
                      '%s: %s' % (book.id, str(book))], positions=positions,
                     after='' if has_next else '_')
    else:
        stdout.p([_('Books'), ''], positions=positions)
