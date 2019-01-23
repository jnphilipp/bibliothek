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

from bindings.models import Binding
from books.models import Edition
from django.core.files import File as DJFile
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _
from files.models import File
from languages.models import Language
from links.models import Link
from persons.models import Person
from publishers.models import Publisher
from utils import lookahead


def create(book, alternate_title=None, isbn=None, publishing_date=None,
           cover_image=None, binding=None, publisher=None, persons=[],
           languages=[], links=[], files=[]):
    edition, created = Edition.objects.get_or_create(
        book=book, isbn=isbn, publishing_date=publishing_date,
        defaults={'isbn': isbn, 'publishing_date': publishing_date})
    if created:
        if alternate_title:
            edition.alternate_title = alternate_title

        if cover_image:
            edition.cover_image.save(os.path.basename(cover_image),
                                     DJFile(open(cover_image, 'rb')))

        if binding:
            edition.binding, c = Binding.objects.filter(
                Q(pk=binding if binding.isdigit() else None) |
                Q(name__icontains=binding)
            ).get_or_create(defaults={'name': binding})

        if publisher:
            edition.publisher, c = Publisher.objects.filter(
                Q(pk=publisher if publisher.isdigit() else None) |
                Q(name__icontains=publisher)
            ).get_or_create(defaults={'name': publisher})

        for (i, p), has_next in lookahead(enumerate(persons)):
            person, c = Person.objects.annotate(
                name=Concat('first_name', Value(' '), 'last_name')
            ).filter(
                Q(pk=p if p.isdigit() else None) | Q(name__icontains=positions)
            ).get_or_create(
                defaults={
                    'first_name': p[:p.rfind(' ')],
                    'last_name': p[p.rfind(' ') + 1:]}
            )
            edition.persons.add(person)

        for (i, l), has_next in lookahead(enumerate(languages)):
            language, c = Language.objects.filter(
                Q(pk=l if l.isdigit() else None) | Q(name=l)
            ).get_or_create(defaults={'name': l})
            edition.languages.add(language)

        for (i, file), has_next in lookahead(enumerate(files)):
            file_name = os.path.basename(file)
            file_obj = File()
            file_obj.file.save(file_name, DJFile(open(file, 'rb')))
            file_obj.content_object = edition
            file_obj.save()

        for (i, l), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(Q(pk=l if l.isdigit() else None) |
                                          Q(link=l)). \
                get_or_create(defaults={'link': l})
            edition.links.add(link)
        edition.save()
    return edition, created


def edit(edition, field, value):
    fields = ['alternate_title', 'alternate-title', 'binding', 'cover', 'isbn',
              'person', 'publishing_date', 'publishing-date', 'publisher',
              'language', 'link', 'file']
    assert field in fields

    if field == 'alternate_title' or field == 'alternate-title':
        edition.alternate_title = value
    elif field == 'binding':
        edition.binding, created = Binding.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)
        ).get_or_create(defaults={'name': value})
    elif field == 'cover':
        edition.cover_image.save(os.path.basename(value),
                                 DJFile(open(value, 'rb')))
    elif field == 'isbn':
        edition.isbn = value
    elif field == 'person':
        person, c = Person.objects.annotate(
            name=Concat('first_name', Value(' '), 'last_name')
        ).filter(
            Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)
        ).get_or_create(
            defaults={
                'first_name': value[:value.rfind(' ')],
                'last_name': value[value.rfind(' ') + 1:]}
        )
        if edition.persons.filter(pk=person.pk).exists():
            edition.persons.remove(person)
        else:
            edition.persons.add(person)
    elif field == 'publishing_date' or field == 'publishing-date':
        edition.publishing_date = value
    elif field == 'publisher':
        edition.publisher, created = Publisher.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)
        ).get_or_create(defaults={'name': value})
    elif field == 'language':
        language, created = Language.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(name=value)
        ).get_or_create(defaults={'name': value})
        if edition.languages.filter(pk=language.pk).exists():
            edition.languages.remove(language)
        else:
            edition.languages.add(language)
    elif field == 'link':
        link, created = Link.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(link=value)
        ).get_or_create(defaults={'link': value})
        if edition.links.filter(pk=link.pk).exists():
            edition.links.remove(link)
        else:
            edition.links.add(link)
    elif field == 'file':
        file_name = os.path.basename(value)
        file_obj = File()
        file_obj.file.save(file_name, DJFile(open(value, 'rb')))
        file_obj.content_object = edition
        file_obj.save()
    edition.save()
