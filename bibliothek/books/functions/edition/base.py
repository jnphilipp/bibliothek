# -*- coding: utf-8 -*-

import os

from bindings.models import Binding
from books.models import Edition
from django.core.files import File as DJFile
from django.db.models import Q
from django.utils.translation import ugettext as _
from files.models import File
from languages.models import Language
from publishers.models import Publisher
from utils import lookahead, stdout


def create(book, isbn=None, published_on=None, cover_image=None, binding=None, publisher=None, languages=[], files=[]):
    positions = [.33, 1.]

    edition, created = Edition.objects.get_or_create(book=book, isbn=isbn, published_on=published_on, defaults={'isbn':isbn, 'published_on':published_on})
    if created:
        stdout.p([_('Id'), edition.id], positions=positions)
        stdout.p([_('Book'), edition.book], positions=positions)

        if cover_image:
            edition.cover_image.save(os.path.basename(cover_image), DJFile(open(cover_image, 'rb')))
            stdout.p([_('Cover image'), cover_image], positions=positions)
        else:
            stdout.p([_('Cover image'), ''], positions=positions)

        if binding:
            edition.binding, c = Binding.objects.filter(Q(pk=binding if binding.isdigit() else None) | Q(name__icontains=binding)).get_or_create(defaults={'name':binding})
            stdout.p([_('Binding'), '%s: %s' % (edition.binding.id, edition.binding.name)], positions=positions)
        else:
            stdout.p([_('Binding'), ''], positions=positions)

        if publisher:
            edition.publisher, c = Publisher.objects.filter(Q(pk=publisher if publisher.isdigit() else None) | Q(name__icontains=publisher)).get_or_create(defaults={'name':publisher})
            stdout.p([_('Publisher'), '%s: %s' % (edition.publisher.id, edition.publisher.name)], positions=positions)
        else:
            stdout.p([_('Publisher'), ''], positions=positions)

        for (i, l), has_next in lookahead(enumerate(languages)):
            language, c = Language.objects.filter(Q(pk=l if l.isdigit() else None) | Q(name=l)).get_or_create(defaults={'name':l})
            edition.languages.add(language)
            stdout.p([_('Languages') if i == 0 else '', '%s: %s' % (language.id, language.name)], after=None if has_next else '_', positions=positions)

        for (i, file), has_next in lookahead(enumerate(files)):
            file_name = os.path.basename(file)
            file_obj = File()
            file_obj.file.save(file_name, DJFile(open(file, 'rb')))
            file_obj.content_object = edition
            file_obj.save()
            stdout.p([_('Files') if i == 0 else '', '%s: %s' % (file_obj.id, file_name)], after=None if has_next else '_', positions=positions)
        edition.save()
        stdout.p([_('Successfully added edition "%(edition)s" with id "%(id)s".') % {'edition':str(edition), 'id':edition.id}], after='=', positions=[1.])
    else:
        stdout.p([_('The edition "%(edition)s" already exists with id "%(id)s", aborting...') % {'edition':str(edition), 'id':edition.id}], after='=', positions=[1.])
    return edition, created


def edit(edition, field, value):
    assert field in ['binding', 'cover', 'isbn', 'published_on', 'publisher', '+language', '-language', '+file']

    if field == 'binding':
        edition.binding, created = Binding.objects.filter(Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)).get_or_create(defaults={'name':value})
    elif field == 'cover':
        edition.cover_image.save(os.path.basename(value), DJFile(open(value, 'rb')))
    elif field == 'isbn':
        edition.isbn = value
    elif field == 'published_on':
        edition.published_on = value
    elif field == 'publisher':
        edition.publisher, created = Publisher.objects.filter(Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)).get_or_create(defaults={'name':value})
    elif field == '+language':
        language, created = Language.objects.filter(Q(pk=value if value.isdigit() else None) | Q(name=value)).get_or_create(defaults={'name':value})
        edition.languages.add(language)
    elif field == '-language':
        try:
            language = Language.objects.get(Q(pk=value if value.isdigit() else None) | Q(name=value))
            edition.languages.remove(language)
        except Language.DoesNotExist:
            stdout.p([_('Language "%(name)s" not found.') % {'name':value}], positions=[1.])
    elif field == '+file':
        file_name = os.path.basename(value)
        file_obj = File()
        file_obj.file.save(file_name, DJFile(open(value, 'rb')))
        file_obj.content_object = edition
        file_obj.save()
    edition.save()
    stdout.p([_('Successfully edited edition "%(edition)s" with id "%(id)s".') % {'edition':str(edition), 'id':edition.id}], positions=[1.])


def info(edition):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), edition.id], positions=positions)
    stdout.p([_('Book'), str(edition.book)], positions=positions)
    stdout.p([_('ISBN'), edition.isbn if edition.isbn else ''], positions=positions)
    stdout.p([_('Published on'), edition.published_on if edition.published_on else ''], positions=positions)
    stdout.p([_('Cover'), edition.cover_image if edition.cover_image else ''], positions=positions)
    stdout.p([_('Binding'), '%s: %s' % (edition.binding.id, edition.binding.name) if edition.binding else ''], positions=positions)
    stdout.p([_('Publisher'), '%s: %s' % (edition.publisher.id, edition.publisher.name) if edition.publisher else ''], positions=positions)

    if edition.files.count() > 0:
        for (i, file), has_next in lookahead(enumerate(edition.files.all())):
            stdout.p([_('Files') if i == 0 else '', '%s: %s' % (file.id, file)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Files'), ''], positions=positions)

    if edition.languages.count() > 0:
        for (i, language), has_next in lookahead(enumerate(edition.languages.all())):
            stdout.p([_('Languages') if i == 0 else '', '%s: %s' % (language.id, language.name)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Languages'), ''], positions=positions)

    if edition.acquisitions.count() > 0:
        for (i, acquisition), has_next in lookahead(enumerate(edition.acquisitions.all())):
            stdout.p([_('Acquisitions') if i == 0 else '', '%s: date=%s, price=%0.2f' % (acquisition.id, acquisition.date, acquisition.price)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Acquisitions'), ''], positions=positions)

    if edition.reads.count() > 0:
        for (i, read), has_next in lookahead(enumerate(edition.reads.all())):
            stdout.p([_('Read') if i == 0 else '', '%s: date started=%s, date finished=%s' % (read.id, read.started, read.finished)], positions=positions, after='' if has_next else '=')
    else:
        stdout.p([_('Read'), ''], positions=positions)
