# -*- coding: utf-8 -*-

import os

from django.core.files import File as DJFile
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from files.models import File
from languages.models import Language
from links.models import Link
from magazines.models import Issue
from utils import lookahead, stdout


def create(magazine, issue_name, published_on=None, cover_image=None, languages=[], links=[], files=[]):
    positions = [.33, 1.]

    issue, created = Issue.objects.get_or_create(magazine=magazine, issue=issue_name)
    if created:
        stdout.p([_('Id'), issue.id], positions=positions)
        stdout.p([_('Issue'), issue.issue], positions=positions)

        if published_on:
            issue.published_on = published_on
            stdout.p([_('Published on'), published_on], positions=positions)
        else:
            stdout.p([_('Published on'), ''], positions=positions)

        if cover_image:
            issue.cover_image = cover_image
            stdout.p([_('Cover image'), cover_image], positions=positions)
        else:
            stdout.p([_('Cover image'), ''], positions=positions)

        for (i, l), has_next in lookahead(enumerate(languages)):
            language, c = Language.objects.filter(Q(pk=l if l.isdigit() else None) | Q(name=l)).get_or_create(defaults={'name':l})
            issue.languages.add(language)
            stdout.p([_('Languages') if i == 0 else '', '%s: %s' % (language.id, language.name)], after=None if has_next else '_', positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(Q(pk=url if url.isdigit() else None) | Q(link=url)).get_or_create(defaults={'link':url})
            issue.links.add(link)
            stdout.p([_('Links') if i == 0 else '', '%s: %s' % (link.id, link.link)], after=None if has_next else '_', positions=positions)

        for (i, file), has_next in lookahead(enumerate(files)):
            file_name = os.path.basename(file)
            file_obj = File()
            file_obj.file.save(file_name, DJFile(open(file, 'rb')))
            file_obj.content_object = issue
            file_obj.save()
            stdout.p([_('Files') if i == 0 else '', '%s: %s' % (file_obj.id, file_name)], after=None if has_next else '_', positions=positions)
        issue.save()
        stdout.p([_('Successfully added issue "%(magazine)s %(issue)s" with id "%(id)s".') % {'magazine':issue.magazine.name, 'issue':issue.issue, 'id':issue.id}], after='=', positions=[1.])
    else:
        stdout.p([_('The issue "%(magazine)s %(issue)s" already exists with id "%(id)s", aborting...') % {'magazine':issue.magazine.name, 'issue':issue.issue, 'id':issue.id}], after='=', positions=[1.])
    return issue, created


def edit(issue, field, value):
    assert field in ['issue', 'published_on', 'cover', '+language', '-language', '+file', '+link', '-link']

    if field == 'issue':
        issue.issue = value
    elif field == 'published_on':
        issue.published_on = value
    elif field == 'cover':
        issue.cover_image = value
    elif field == '+language':
        language, created = Language.objects.filter(Q(pk=value if value.isdigit() else None) | Q(name=value)).get_or_create(defaults={'name':value})
        issue.languages.add(language)
    elif field == '-language':
        try:
            language = Language.objects.get(Q(pk=value if value.isdigit() else None) | Q(name=value))
            issue.languages.remove(language)
        except Language.DoesNotExist:
            stdout.p([_('Language "%(name)s" not found.') % {'name':value}], positions=[1.])
    elif field == '+file':
        file_name = os.path.basename(value)
        file_obj = File()
        file_obj.file.save(file_name, DJFile(open(value, 'rb')))
        file_obj.content_object = issue
        file_obj.save()
    elif field == '+link':
        link, created = Link.objects.filter(Q(pk=value if value.isdigit() else None) | Q(link=value)).get_or_create(defaults={'link':value})
        issue.links.add(link)
    elif field == '-link':
        try:
            link = Link.objects.get(Q(pk=value if value.isdigit() else None) | Q(link=value))
            issue.links.remove(link)
        except Link.DoesNotExist:
            stdout.p([_('Link "%(link)s" not found.') % {'link':value}], positions=[1.])
    issue.save()
    stdout.p([_('Successfully edited issue "%(magazine)s %(issue)s" with id "%(id)s".') % {'magazine':issue.magazine.name, 'issue':issue.issue, 'id':issue.id}], positions=[1.])


def info(issue):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), issue.id], positions=positions)
    stdout.p([_('Magazine'), '%s: %s' % (issue.magazine.id, issue.magazine.name)], positions=positions)
    stdout.p([_('Issue'), issue.issue], positions=positions)
    stdout.p([_('Published on'), issue.published_on if issue.published_on else ''], positions=positions)
    stdout.p([_('Cover'), issue.cover_image.name if issue.cover_image else ''], positions=positions)

    if issue.languages.count() > 0:
        for (i, language), has_next in lookahead(enumerate(issue.languages.all())):
            stdout.p([_('Languages') if i == 0 else '', '%s: %s' % (language.id, language.name)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Languages'), ''], positions=positions)

    if issue.files.count() > 0:
        for (i, file), has_next in lookahead(enumerate(issue.files.all())):
            stdout.p([_('Files') if i == 0 else '', '%s: %s' % (file.id, file)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Files'), ''], positions=positions)

    if issue.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(issue.links.all())):
            stdout.p([_('Links') if i == 0 else '', '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)

    if issue.acquisitions.count() > 0:
        for (i, acquisition), has_next in lookahead(enumerate(issue.acquisitions.all())):
            stdout.p([_('Acquisitions') if i == 0 else '', '%s: date=%s, price=%0.2f' % (acquisition.id, acquisition.date, acquisition.price)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Acquisitions'), ''], positions=positions)

    if issue.reads.count() > 0:
        for (i, read), has_next in lookahead(enumerate(issue.reads.all())):
            stdout.p([_('Read') if i == 0 else '', '%s: date started=%s, date finished=%s' % (read.id, read.started, read.finished)], positions=positions, after='' if has_next else '=')
    else:
        stdout.p([_('Read'), ''], positions=positions)
