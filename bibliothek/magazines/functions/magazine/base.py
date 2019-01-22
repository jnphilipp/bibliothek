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
from magazines.models import Magazine
from utils import lookahead, stdout


def create(name, feed=None, links=[]):
    positions = [.33, 1.]

    magazine, created = Magazine.objects.get_or_create(name=name)
    if created:
        stdout.p([_('Id'), magazine.id], positions=positions)
        stdout.p([_('Name'), magazine.name], positions=positions)

        if feed:
            magazine.feed, c = Link.objects.filter(
                Q(pk=feed if feed.isdigit() else None) | Q(link=feed)
            ).get_or_create(defaults={'link': feed})
            stdout.p([_('Feed'),
                      '%s: %s' % (magazine.feed.id, magazine.feed.link)],
                     positions=positions)
        else:
            stdout.p([_('Feed'), ''], positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(
                Q(pk=url if url.isdigit() else None) | Q(link=url)
            ).get_or_create(defaults={'link': url})
            magazine.links.add(link)
            stdout.p([_('Links') if i == 0 else '',
                      '%s: %s' % (link.id, link.link)],
                     after=None if has_next else '_', positions=positions)
        magazine.save()
        msg = _('Successfully added magazine "%(name)s" with id "%(id)s".')
        stdout.p([msg % {'name': magazine.name, 'id': magazine.id}], after='=',
                 positions=[1.])
    else:
        msg = _('The magazine "%(name)s" already exists with id "%(id)s", ' +
                'aborting...')
        stdout.p([msg % {'name': magazine.name, 'id': magazine.id}], after='=',
                 positions=[1.])
    return magazine, created


def delete(magazine):
    msg = _('Deleting magazine "%(name)s" with id "%(id)s".')
    stdout.p([msg % {'name': magazine.name, 'id': magazine.id}],
             positions=[1.])

    positions = [.1, .25, 1.]
    if magazine.issues.count() > 0:
        stdout.p([_('Deleting the issues:')], positions=[1.])
        stdout.p([_('Id'), _('Related object'), _('Issue')],
                 positions=positions, after='=')

        issues = magazine.issues.all().order_by('publishing_date')
        for (i, issue), has_next in lookahead(enumerate(issues)):
            stdout.p([issue.id, '', issue.issue], positions=positions,
                     after='')

            if issue.files.count() > 0:
                for i, file in enumerate(issue.files.all()):
                    stdout.p(['', _('Files') if i == 0 else '',
                              '%s: %s' % (file.id, file)], positions=positions,
                             after='')
                    file.delete()
            else:
                stdout.p(['', _('Files'), ''], positions=positions, after='')

            if issue.links.count() > 0:
                for i, link in enumerate(issue.links.all()):
                    stdout.p(['', _('Links') if i == 0 else '',
                              '%s: %s' % (link.id, link.link)],
                             positions=positions, after='')
                    links.delete()
            else:
                stdout.p(['', _('Links'), ''], positions=positions, after='')

            if issue.acquisitions.count() > 0:
                date_trans = _('date')
                price_trans = _('price')
                for i, acquisition in enumerate(issue.acquisitions.all()):
                    stdout.p(['', _('Acquisitions') if i == 0 else '',
                              '%s: %s=%s, %s=%0.2f' % (acquisition.id,
                                                       date_trans,
                                                       acquisition.date,
                                                       price_trans,
                                                       acquisition.price)],
                             positions=positions, after='')
                    acquisition.delete()
            else:
                stdout.p(['', _('Acquisitions'), ''], positions=positions,
                         after='')

            if issue.reads.count() > 0:
                date_started_trans = _('date started')
                date_finished_trans = _('date finished')
                for i, read in enumerate(issue.reads.all()):
                    stdout.p(['', _('Read') if i == 0 else '',
                              '%s: %s=%s, %s=%s' % (read.id,
                                                    date_started_trans,
                                                    read.started,
                                                    date_finished_trans,
                                                    read.finished)],
                             positions=positions,
                             after='_' if has_next else '=')
                    read.delete()
            else:
                stdout.p(['', _('Read'), ''], positions=positions,
                         after='_' if has_next else '=')
            issue.delete()
    else:
        stdout.p([_('No issues to delete.')], positions=[1.])
    magazine.delete()


def edit(magazine, field, value):
    assert field in ['name', 'feed', 'link']

    if field == 'name':
        magazine.name = value
    elif field == 'feed':
        magazine.feed, created = Link.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(link=value)
        ).get_or_create(defaults={'link': value})
    elif field == 'link':
        link, created = Link.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(link=value)
        ).get_or_create(defaults={'link': value})
        if magazine.links.filter(pk=link.pk).exists():
            magazine.links.remove(link)
        else:
            magazine.links.add(link)
    magazine.save()
    msg = _('Successfully edited magazine "%(name)s" with id "%(id)s".')
    stdout.p([msg % {'name': magazine.name, 'id': magazine.id}],
             positions=[1.])


def info(magazine):
    positions = [.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), magazine.id], positions=positions)
    stdout.p([_('Name'), magazine.name], positions=positions)
    stdout.p([_('Feed'),
              '%s: %s' % (magazine.feed.id,
                          magazine.feed.link) if magazine.feed else ''],
             positions=positions)

    if magazine.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(magazine.links.all())):
            if i == 0:
                stdout.p([_('Links'), '%s: %s' % (link.id, link.link)],
                         positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (link.id, link.link)],
                         positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)

    if magazine.issues.count() > 0:
        issues = magazine.issues.all().order_by('publishing_date')
        for (i, issue), has_next in lookahead(enumerate(issues)):
            if i == 0:
                stdout.p([_('Issue'), '%s: %s' % (issue.id, issue.issue)],
                         positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (issue.id, issue.issue)],
                         positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Issue'), ''], positions=positions)
