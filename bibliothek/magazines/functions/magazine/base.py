# -*- coding: utf-8 -*-

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
            magazine.feed, c = Link.objects.filter(Q(pk=feed if feed.isdigit() else None) | Q(link=feed)).get_or_create(defaults={'link':feed})
            stdout.p([_('Feed'), '%s: %s' % (magazine.feed.id, magazine.feed.link)], positions=positions)
        else:
            stdout.p([_('Feed'), ''], positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(Q(pk=url if url.isdigit() else None) | Q(link=url)).get_or_create(defaults={'link':url})
            magazine.links.add(link)
            stdout.p([_('Links') if i == 0 else '', '%s: %s' % (link.id, link.link)], after=None if has_next else '_', positions=positions)
        magazine.save()
        stdout.p([_('Successfully added magazine "%(name)s" with id "%(id)s".') % {'name':magazine.name, 'id':magazine.id}], after='=', positions=[1.])
    else:
        stdout.p([_('The magazine "%(name)s" already exists with id "%(id)s", aborting...') % {'name':magazine.name, 'id':magazine.id}], after='=', positions=[1.])
    return magazine, created


def delete(magazine):
    stdout.p([_('Deleting magazine "%(name)s" with id "%(id)s".') % {'name': magazine.name, 'id': magazine.id}], positions=[1.])

    positions=[.1, .25, 1.]
    if magazine.issues.count() > 0:
        stdout.p([_('Deleting the issues:')], positions=[1.])
        stdout.p([_('Id'), _('Related object'), _('Issue')], positions=positions, after='=')
        for (i, issue), has_next in lookahead(enumerate(magazine.issues.all().order_by('published_on'))):
            stdout.p([issue.id, '', issue.issue], positions=positions, after='')

            if issue.files.count() > 0:
                for i, file in enumerate(issue.files.all()):
                    stdout.p(['', _('Files') if i == 0 else '', '%s: %s' % (file.id, file)], positions=positions, after='')
                    file.delete()
            else:
                stdout.p(['', _('Files'), ''], positions=positions, after='')

            if issue.links.count() > 0:
                for i, link in enumerate(issue.links.all()):
                    stdout.p(['', _('Links') if i == 0 else '', '%s: %s' % (link.id, link.link)], positions=positions, after='')
                    links.delete()
            else:
                stdout.p(['', _('Links'), ''], positions=positions, after='')

            if issue.acquisitions.count() > 0:
                for i, acquisition in enumerate(issue.acquisitions.all()):
                    stdout.p(['', _('Acquisitions') if i == 0 else '', '%s: date=%s, price=%0.2f' % (acquisition.id, acquisition.date, acquisition.price)], positions=positions, after='')
                    acquisition.delete()
            else:
                stdout.p(['', _('Acquisitions'), ''], positions=positions, after='')

            if issue.reads.count() > 0:
                for i, read in enumerate(issue.reads.all()):
                    stdout.p(['', _('Read') if i == 0 else '', '%s: date started=%s, date finished=%s' % (read.id, read.started, read.finished)], positions=positions, after='_' if has_next else '=')
                    read.delete()
            else:
                stdout.p(['', _('Read'), ''], positions=positions, after='_' if has_next else '=')
            issue.delete()
    else:
        stdout.p([_('No issues to delete.')], positions=[1.])
    magazine.delete()


def edit(magazine, field, value):
    assert field in ['name', 'feed']

    if field == 'name':
        magazine.name = value
    elif field == 'feed':
        magazine.feed, created = Link.objects.filter(Q(pk=value if value.isdigit() else None) | Q(link=value)).get_or_create(defaults={'link':value})
    magazine.save()
    stdout.p([_('Successfully edited magazine "%(name)s" with id "%(id)s".') % {'name':magazine.name, 'id':magazine.id}], positions=[1.])


def info(magazine):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), magazine.id], positions=positions)
    stdout.p([_('Name'), magazine.name], positions=positions)
    stdout.p([_('Feed'), '%s: %s' % (magazine.feed.id, magazine.feed.link) if magazine.feed else ''], positions=positions)

    if magazine.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(magazine.links.all())):
            if i == 0:
                stdout.p([_('Links'), '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)

    if magazine.issues.count() > 0:
        for (i, issue), has_next in lookahead(enumerate(magazine.issues.all().order_by('published_on'))):
            if i == 0:
                stdout.p([_('Issue'), '%s: %s' % (issue.id, issue.issue)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (issue.id, issue.issue)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Issue'), ''], positions=positions)
