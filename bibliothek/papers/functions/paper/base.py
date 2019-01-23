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
from django.db.models import Q, Value
from django.db.models.functions import Concat
from files.models import File
from journals.models import Journal
from languages.models import Language
from links.models import Link
from papers.models import Paper
from persons.models import Person
from utils import lookahead


def create(title, authors=[], publishing_date=None, journal=None, volume=None,
           languages=[], links=[]):
    paper, created = Paper.objects.get_or_create(title=title)
    if created:
        if len(authors) > 0:
            for (i, a), has_next in lookahead(enumerate(authors)):
                author, c = Person.objects.annotate(
                    name=Concat('first_name', Value(' '), 'last_name')
                ).filter(
                    Q(pk=a if a.isdigit() else None) | Q(name__icontains=a)
                ).get_or_create(defaults={
                    'first_name': a[:a.rfind(' ')],
                    'last_name': a[a.rfind(' ') + 1:]
                })
                paper.authors.add(author)

        if publishing_date:
            paper.publishing_date = publishing_date

        if journal:
            paper.journal, c = Journal.objects.filter(
                Q(pk=journal if journal.isdigit() else None) |
                Q(name__icontains=journal)
            ).get_or_create(defaults={'name': journal})

        if volume:
            paper.volume = volume

        for (i, l), has_next in lookahead(enumerate(languages)):
            language, c = Language.objects.filter(
                Q(pk=l if l.isdigit() else None) | Q(name=l)
            ).get_or_create(defaults={'name': l})
            paper.languages.add(language)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(
                Q(pk=url if url.isdigit() else None) | Q(link=url)
            ).get_or_create(defaults={'link': url})
            paper.links.add(link)
        paper.save()
    return paper, created


def edit(paper, field, value):
    fields = ['title', 'author', 'publishing_date', 'publishing-date',
              'journal', 'volume', 'language', 'file', 'link']
    assert field in fields

    if field == 'title':
        paper.title = value
    elif field == 'author':
        author, created = Person.objects.annotate(
            name=Concat('first_name', Value(' '), 'last_name')
        ).filter(
            Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)
        ).get_or_create(defaults={
            'first_name': value[:value.rfind(' ')],
            'last_name': value[value.rfind(' ') + 1:]
        })
        if paper.authors.filter(pk=author.pk).exists():
            paper.authors.remove(author)
        else:
            paper.authors.add(author)
    elif field == 'publishing_date' or field == 'publishing-date':
        paper.publishing_date = value
    elif field == 'journal':
        paper.journal, c = Journal.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)
        ).get_or_create(defaults={'name': value})
    elif field == 'volume':
        paper.volume = value
    elif field == 'language':
        language, created = Language.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(name=value)
        ).get_or_create(defaults={'name': value})
        if paper.languages.filter(pk=language.pk).exists():
            paper.languages.remove(language)
        else:
            paper.languages.add(language)
    elif field == 'link':
        link, created = Link.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(link=value)
        ).get_or_create(defaults={'link': value})
        if paper.links.filter(pk=link.pk).exists():
            paper.links.remove(link)
        else:
            paper.links.add(link)
    elif field == 'file':
        file_name = os.path.basename(value)
        file_obj = File()
        file_obj.file.save(file_name, DJFile(open(value, 'rb')))
        file_obj.content_object = paper
        file_obj.save()
    paper.save()
