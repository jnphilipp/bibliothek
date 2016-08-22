# -*- coding: utf-8 -*-

import os

from django.core.files import File as DJFile
from django.db.models import Q
from django.utils.translation import ugettext as _
from files.models import File
from links.models import Link
from magazines.models import Issue
from utils import lookahead, stdout


def create(magazine, issue_name, published_on=None, cover_image=None, links=[], files=[]):
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
    assert field in ['issue', 'published_on', 'cover']

    if field == 'issue':
        issue.issue = value
    elif field == 'published_on':
        issue.published_on = value
    elif field == 'cover':
        issue.cover_image = value
    issue.save()
    stdout.p([_('Successfully edited issue "%(magazine)s %(issue)s" with id "%(id)s".') % {'magazine':issue.magazine.name, 'issue':issue.issue, 'id':issue.id}], positions=[1.])


def show(issue):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), issue.id], positions=positions)
    stdout.p([_('Magazine'), '%s: %s' % (issue.magazine.id, issue.magazine.name)], positions=positions)
    stdout.p([_('Issue'), issue.issue], positions=positions)
    stdout.p([_('Published on'), issue.published_on], positions=positions)

    if issue.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(issue.links.all())):
            if i == 0:
                stdout.p([_('Links'), '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)

    if issue.files.count() > 0:
        for (i, file), has_next in lookahead(enumerate(issue.files.all())):
            if i == 0:
                stdout.p([_('Files'), '%s: %s' % (file.id, file)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (file.id, file)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Files'), ''], positions=positions)

    if issue.acquisitions.count() > 0:
        for (i, acquisition), has_next in lookahead(enumerate(issue.acquisitions.all())):
            if i == 0:
                stdout.p([_('Acquisitions'), '%s: date=%s, price=%0.2f' % (acquisition.id, acquisition.date, acquisition.price)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: date=%s, price=%0.2f' % (acquisition.id, acquisition.date, acquisition.price)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Acquisitions'), ''], positions=positions)

    if issue.reads.count() > 0:
        for (i, read), has_next in lookahead(enumerate(issue.reads.all())):
            if i == 0:
                stdout.p([_('Read'), '%s: date started=%s, date finished=%s' % (read.id, read.started, read.finished)], positions=positions, after='' if has_next else '=')
            else:
                stdout.p(['', '%s: date started=%s, date finished=%s' % (read.id, read.started, read.finished)], positions=positions, after='' if has_next else '=')
    else:
        stdout.p([_('Read'), ''], positions=positions, after='=')
