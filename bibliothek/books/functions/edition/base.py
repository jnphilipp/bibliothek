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
from utils import lookahead, stdout


def create(book, alternate_title=None, isbn=None, publishing_date=None,
           cover_image=None, binding=None, publisher=None, persons=[],
           languages=[], links=[], files=[]):
    positions = [.33]

    edition, created = Edition.objects.get_or_create(
        book=book,
        isbn=isbn,
        publishing_date=publishing_date,
        defaults={
            'isbn': isbn,
            'publishing_date': publishing_date
        }
    )
    if created:
        stdout.p([_('Id'), edition.id], positions=positions)
        stdout.p([_('Book'), edition.book], positions=positions)
        stdout.p([_('ISBN'), edition.isbn], positions=positions)
        stdout.p([_('Publishing date'), edition.publishing_date],
                 positions=positions)

        if alternate_title:
            edition.alternate_title = alternate_title
            stdout.p([_('Alternate title'), alternate_title],
                     positions=positions)
        else:
            stdout.p([_('Alternate title'), ''], positions=positions)

        if cover_image:
            edition.cover_image.save(os.path.basename(cover_image),
                                     DJFile(open(cover_image, 'rb')))
            stdout.p([_('Cover image'), cover_image], positions=positions)
        else:
            stdout.p([_('Cover image'), ''], positions=positions)

        if binding:
            edition.binding, c = Binding.objects.filter(
                Q(pk=binding if binding.isdigit() else None) |
                Q(name__icontains=binding)
            ).get_or_create(defaults={'name': binding})
            stdout.p([_('Binding'),
                      '%s: %s' % (edition.binding.id, edition.binding.name)],
                     positions=positions)
        else:
            stdout.p([_('Binding'), ''], positions=positions)

        if publisher:
            edition.publisher, c = Publisher.objects.filter(
                Q(pk=publisher if publisher.isdigit() else None) |
                Q(name__icontains=publisher)
            ).get_or_create(defaults={'name': publisher})
            stdout.p([_('Publisher'),
                      '%s: %s' % (edition.publisher.id,
                                  edition.publisher.name)],
                     positions=positions)
        else:
            stdout.p([_('Publisher'), ''], positions=positions)

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
            stdout.p([_('Persons') if i == 0 else '',
                      '%s: %s' % (persons.id, str(persons))],
                     after=None if has_next else '_', positions=positions)

        for (i, l), has_next in lookahead(enumerate(languages)):
            language, c = Language.objects.filter(
                Q(pk=l if l.isdigit() else None) | Q(name=l)
            ).get_or_create(defaults={'name': l})
            edition.languages.add(language)
            stdout.p([_('Languages') if i == 0 else '',
                      '%s: %s' % (language.id, language.name)],
                     after=None if has_next else '_', positions=positions)

        for (i, file), has_next in lookahead(enumerate(files)):
            file_name = os.path.basename(file)
            file_obj = File()
            file_obj.file.save(file_name, DJFile(open(file, 'rb')))
            file_obj.content_object = edition
            file_obj.save()
            stdout.p([_('Files') if i == 0 else '',
                      '%s: %s' % (file_obj.id, file_name)],
                     after=None if has_next else '_', positions=positions)
        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(
                Q(pk=url if url.isdigit() else None) | Q(link=url)
            ).get_or_create(defaults={'link': url})
            edition.links.add(link)
            stdout.p([_('Links') if i == 0 else '',
                      '%s: %s' % (link.id, link.link)],
                     after=None if has_next else '_', positions=positions)
        edition.save()

        msg = _('Successfully added edition "%(edition)s" with id "%(id)s".')
        stdout.p([msg % {'edition': str(edition), 'id': edition.id}],
                 after='=')
    else:
        msg = _('The edition "%(edition)s" already exists with id "%(id)s", ' +
                'aborting...')
        stdout.p([msg % {'edition': str(edition), 'id': edition.id}],
                 after='=')
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

    msg = _('Successfully edited edition "%(edition)s" with id "%(id)s".')
    stdout.p([msg % {'edition': str(edition), 'id': edition.id}])


def info(edition):
    positions = [.33]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), edition.id], positions=positions)
    stdout.p([_('Book'), str(edition.book)], positions=positions)
    stdout.p([_('Alternate title'),
              edition.alternate_title if edition.alternate_title else ''],
             positions=positions)
    stdout.p([_('ISBN'), edition.isbn if edition.isbn else ''],
             positions=positions)
    stdout.p([_('Publishing date'),
              edition.publishing_date if edition.publishing_date else ''],
             positions=positions)
    stdout.p([_('Cover'), edition.cover_image if edition.cover_image else ''],
             positions=positions)
    stdout.p([_('Binding'),
              '%s: %s' % (edition.binding.id,
                          edition.binding.name) if edition.binding else ''],
             positions=positions)
    stdout.p([_('Publisher'),
              '%s: %s' % (edition.publisher.id,
                          edition.publisher.name) if edition.publisher
              else ''],
             positions=positions)

    if edition.persons.count() > 0:
        persons = edition.persons.all()
        for (i, person), has_next in lookahead(enumerate(persons)):
            stdout.p([_('Persons') if i == 0 else '',
                      '%s: %s' % (person.id, str(person))],
                     positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Persons'), ''], positions=positions)

    if edition.languages.count() > 0:
        languages = edition.languages.all()
        for (i, language), has_next in lookahead(enumerate(languages)):
            stdout.p([_('Languages') if i == 0 else '',
                      '%s: %s' % (language.id, language.name)],
                     positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Languages'), ''], positions=positions)

    if edition.links.count() > 0:
        links = edition.links.all()
        for (i, link), has_next in lookahead(enumerate(links)):
            stdout.p([_('Links') if i == 0 else '',
                      '%s: %s' % (link.id, link.link)],
                     positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)

    if edition.files.count() > 0:
        for (i, file), has_next in lookahead(enumerate(edition.files.all())):
            stdout.p([_('Files') if i == 0 else '',
                      '%s: %s' % (file.id, file)],
                     positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Files'), ''], positions=positions)

    if edition.acquisitions.count() > 0:
        acquisitions = edition.acquisitions.all()
        date_trans = _('date')
        price_trans = _('price')
        for (i, acquisition), has_next in lookahead(enumerate(acquisitions)):
            stdout.p([_('Acquisitions') if i == 0 else '',
                      '%s: %s=%s, %s=%0.2f' % (acquisition.id, date_trans,
                                               acquisition.date, price_trans,
                                               acquisition.price)],
                     positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Acquisitions'), ''], positions=positions)

    if edition.reads.count() > 0:
        date_started_trans = _('date started')
        date_finished_trans = _('date finished')
        for (i, read), has_next in lookahead(enumerate(edition.reads.all())):
            stdout.p([_('Read') if i == 0 else '',
                      '%s: %s=%s, %s=%s' % (read.id, date_started_trans,
                                            read.started, date_finished_trans,
                                            read.finished)],
                     positions=positions, after='' if has_next else '=')
    else:
        stdout.p([_('Read'), ''], positions=positions)
