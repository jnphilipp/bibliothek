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

import os

from django.core.files import File as DJFile
from django.db.models import Q
from files.models import File
from languages.models import Language
from links.models import Link
from magazines.models import Issue
from utils import lookahead


def create(magazine, issue_name, publishing_date=None, cover_image=None,
           languages=[], links=[], files=[]):
    issue, created = Issue.objects.get_or_create(magazine=magazine,
                                                 issue=issue_name)
    if created:
        if publishing_date:
            issue.publishing_date = publishing_date

        if cover_image:
            issue.cover_image.save(os.path.basename(cover_image),
                                   DJFile(open(cover_image, 'rb')))

        for (i, l), has_next in lookahead(enumerate(languages)):
            language, c = Language.objects.filter(
                Q(pk=l if l.isdigit() else None) | Q(name=l)
            ).get_or_create(defaults={'name': l})
            issue.languages.add(language)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(
                Q(pk=url if url.isdigit() else None) | Q(link=url)
            ).get_or_create(defaults={'link': url})
            issue.links.add(link)

        for (i, file), has_next in lookahead(enumerate(files)):
            file_name = os.path.basename(file)
            file_obj = File()
            file_obj.file.save(file_name, DJFile(open(file, 'rb')))
            file_obj.content_object = issue
            file_obj.save()
        issue.save()
    return issue, created


def edit(issue, field, value):
    fields = ['issue', 'publishing_date', 'publishing-date', 'cover',
              'language', 'file', 'link']
    assert field in fields

    if field == 'issue':
        issue.issue = value
    elif field == 'publishing_date' or field == 'publishing-date':
        issue.publishing_date = value
    elif field == 'cover':
        issue.cover_image = value
    elif field == 'language':
        language, created = Language.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(name=value)
        ).get_or_create(defaults={'name': value})
        if issue.languages.filter(pk=language.pk).exists():
            issue.languages.remove(language)
        else:
            issue.languages.add(language)
    elif field == 'file':
        file_name = os.path.basename(value)
        file_obj = File()
        file_obj.file.save(file_name, DJFile(open(value, 'rb')))
        file_obj.content_object = issue
        file_obj.save()
    elif field == 'link':
        link, created = Link.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(link=value)
        ).get_or_create(defaults={'link': value})
        if issue.links.filter(pk=link.pk).exists():
            issue.links.remove(link)
        else:
            issue.links.add(link)
    issue.save()
