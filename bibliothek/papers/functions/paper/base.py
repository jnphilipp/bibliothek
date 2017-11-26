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

import os

from django.core.files import File as DJFile
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _
from files.models import File
from journals.models import Journal
from languages.models import Language
from links.models import Link
from papers.models import Paper
from persons.models import Person
from utils import lookahead, stdout


def create(title, authors=[], publishing_date=None, journal=None, volume=None,
           languages=[], links=[]):
    positions = [.33, 1.]

    paper, created = Paper.objects.get_or_create(title=title)
    if created:
        stdout.p([_('Id'), paper.id], positions=positions)
        stdout.p([_('Title'), paper.title], positions=positions)

        if len(authors) > 0:
            for (i, a), has_next in lookahead(enumerate(authors)):
                author, c = Person.objects.annotate(
                    name=Concat('first_name', Value(' '), 'last_name')
                ).filter(
                    Q(pk=a if a.isdigit() else None) | Q(name__icontains=a)
                ).get_or_create(defaults={
                    'first_name': a[:a.rfind(' ')],
                    'last_name': a[a.rfind(' ') + 1 :]
                })
                paper.authors.add(author)
                stdout.p([_('Authors') if i == 0 else '',
                          '%s: %s' % (author.id, str(author))],
                         after=None if has_next else '_', positions=positions)
        else:
            stdout.p([_('Authors'), ''], positions=positions)

        if publishing_date:
            paper.publishing_date = publishing_date
            stdout.p([_('Publishing date'), paper.publishing_date],
                     positions=positions)
        else:
            stdout.p([_('Publishing date'), ''], positions=positions)

        if journal:
            paper.journal, c = Journal.objects.filter(
                Q(pk=journal if journal.isdigit() else None) |
                Q(name__icontains=journal)
            ).get_or_create(defaults={'name': journal})
            stdout.p([_('Journal'), '%s: %s' % (paper.journal.id,
                                                paper.journal.name)],
                     positions=positions)
        else:
            stdout.p([_('Journal'), ''], positions=positions)

        if volume:
            paper.volume = volume
            stdout.p([_('Volume'), paper.volume], positions=positions)
        else:
            stdout.p([_('Volume'), ''], positions=positions)

        for (i, l), has_next in lookahead(enumerate(languages)):
            language, c = Language.objects.filter(
                Q(pk=l if l.isdigit() else None) | Q(name=l)
            ).get_or_create(defaults={'name': l})
            paper.languages.add(language)
            stdout.p([_('Languages') if i == 0 else '',
                      '%s: %s' % (language.id, language.name)],
                     after=None if has_next else '_', positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(
                Q(pk=url if url.isdigit() else None) | Q(link=url)
            ).get_or_create(defaults={'link': url})
            paper.links.add(link)
            stdout.p([_('Links') if i == 0 else '',
                      '%s: %s' % (link.id, link.link)],
                     after=None if has_next else '_', positions=positions)

        paper.save()
        msg = _('Successfully added paper "%(title)s" with id "%(id)s".')
        stdout.p([msg % {'title':paper.title, 'id':paper.id}], after='=',
                 positions=[1.])
    else:
        msg = _('The paper "%(title)s" already exists with id "%(id)s", ' +
                'aborting...')
        stdout.p([msg % {'title':paper.title, 'id':paper.id}], after='=',
                 positions=[1.])
    return paper, created


def edit(paper, field, value):
    fields = ['title', '+author', '-author', 'publishing_date',
              'publishing-date', 'journal', 'volume', '+language', '-language',
              '+file', '+link']
    assert field in fields

    if field == 'title':
        paper.title = value
    elif field == '+author':
        author, created = Person.objects.annotate(
            name=Concat('first_name', Value(' '), 'last_name')
        ).filter(
            Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)
        ).get_or_create(defaults={
            'first_name': value[:value.rfind(' ')],
            'last_name': value[value.rfind(' ') + 1 :]
        })
        paper.authors.add(author)
    elif field == '-author':
        try:
            author = Person.objects.annotate(
                name=Concat('first_name', Value(' '), 'last_name')
            ).get(
                Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)
            )
            paper.authors.remove(author)
        except Person.DoesNotExist:
            stdout.p([_('Author "%(name)s" not found.') % {'name': value}],
                     positions=[1.])
    elif field == 'publishing_date' or field == 'publishing-date':
        paper.publishing_date = value
    elif field == 'journal':
        paper.journal, c = Journal.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)
        ).get_or_create(defaults={'name': value})
    elif field == 'volume':
        paper.volume = value
    elif field == '+language':
        language, created = Language.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(name=value)
        ).get_or_create(defaults={'name': value})
        paper.languages.add(language)
    elif field == '-language':
        try:
            language = Language.objects.get(
                Q(pk=value if value.isdigit() else None) | Q(name=value)
            )
            paper.languages.remove(language)
        except Language.DoesNotExist:
            stdout.p([_('Language "%(name)s" not found.') % {'name': value}],
                     positions=[1.])
    elif field == '+link':
        link, created = Link.objects.filter(
            Q(pk=value if value.isdigit() else None) | Q(link=value)
        ).get_or_create(defaults={'link': value})
        paper.links.add(link)
    elif field == '+file':
        file_name = os.path.basename(value)
        file_obj = File()
        file_obj.file.save(file_name, DJFile(open(value, 'rb')))
        file_obj.content_object = paper
        file_obj.save()
    paper.save()
    msg = _('Successfully edited paper "%(title)s" with id "%(id)s".')
    stdout.p([msg % {'title':paper.title, 'id':paper.id}], positions=[1.])


def info(paper):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), paper.id], positions=positions)
    stdout.p([_('Title'), paper.title], positions=positions)

    if paper.authors.count() > 0:
        for (i, author), has_next in lookahead(enumerate(paper.authors.all())):
            if i == 0:
                stdout.p([_('Authors'), '%s: %s' % (author.id, str(author))],
                         positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (author.id, str(author))],
                         positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Authors'), ''], positions=positions)

    stdout.p([_('Journal'),
              '%s: %s' % (paper.journal.id,
                          paper.journal.name) if paper.journal else ''],
             positions=positions)
    stdout.p([_('Volume'), paper.volume if paper.volume else ''],
             positions=positions)
    stdout.p([_('Publishing date'), paper.publishing_date],
             positions=positions)

    if paper.languages.count() > 0:
        languages = paper.languages.all()
        for (i, language), has_next in lookahead(enumerate(languages)):
            if i == 0:
                stdout.p([_('Languages'), language], positions=positions,
                         after='' if has_next else '_')
            else:
                stdout.p(['', language], positions=positions,
                         after='' if has_next else '_')
    else:
        stdout.p([_('Languages'), ''], positions=positions)

    if paper.files.count() > 0:
        for (i, file), has_next in lookahead(enumerate(paper.files.all())):
            if i == 0:
                stdout.p([_('Files'), '%s: %s' % (file.id, file)],
                         positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (file.id, file)],
                         positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Files'), ''], positions=positions)

    if paper.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(paper.links.all())):
            if i == 0:
                stdout.p([_('Links'), '%s: %s' % (link.id, link.link)],
                         positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (link.id, link.link)],
                         positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)

    if paper.acquisitions.count() > 0:
        acquisitions = paper.acquisitions.all()
        date_trans = _('date')
        price_trans = _('price')
        for (i, acquisition), has_next in lookahead(enumerate(acquisitions)):
            if i == 0:
                stdout.p([
                    _('Acquisitions'),
                    '%s: %s=%s, %s=%0.2f' % (acquisition.id, date_trans,
                                             acquisition.date, price_trans,
                                             acquisition.price)
                ], positions=positions, after='' if has_next else '_')
            else:
                stdout.p([+
                    '',
                    '%s: %s=%s, %s=%0.2f' % (acquisition.id, date_trans,
                                             acquisition.date, price_trans,
                                             acquisition.price)
                ], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Acquisitions'), ''], positions=positions)

    if paper.reads.count() > 0:
        date_started_trans = _('date started')
        date_finished_trans = _('date finished')
        for (i, read), has_next in lookahead(enumerate(paper.reads.all())):
            if i == 0:
                stdout.p([
                    _('Reads'),
                    '%s: %s=%s, %s=%s' % (read.id, date_started_trans,
                                          read.started, date_finished_trans,
                                          read.finished)
                ], positions=positions, after='' if has_next else '=')
            else:
                stdout.p([
                    '',
                    '%s: %s=%s, %s=%s' % (read.id, date_started_trans,
                                          read.started, date_finished_trans,
                                          read.finished)
                ], positions=positions, after='' if has_next else '=')
    else:
        stdout.p([_('Reads'), ''], positions=positions, after='=')
