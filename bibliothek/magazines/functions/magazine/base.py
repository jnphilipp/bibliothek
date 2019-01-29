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
from links.models import Link
from magazines.models import Magazine
from utils import lookahead


def create(name, feed=None, links=[]):
    magazine, created = Magazine.objects.get_or_create(name=name)
    if created:
        if feed:
            magazine.feed, c = Link.objects.filter(
                Q(pk=feed if feed.isdigit() else None) | Q(link=feed)
            ).get_or_create(defaults={'link': feed})

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(
                Q(pk=url if url.isdigit() else None) | Q(link=url)
            ).get_or_create(defaults={'link': url})
            magazine.links.add(link)
        magazine.save()
    return magazine, created


def delete(magazine):
    for issue in magazine.issues.all():
        for file in issue.files.all():
                file.delete()

        for link in issue.links.all():
            link.delete()

        for acquisition in issue.acquisitions.all():
            acquisition.delete()

        for read in issue.reads.all():
            read.delete()
        issue.delete()
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
