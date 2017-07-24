# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from links.models import Link
from publishers.models import Publisher
from utils import lookahead, stdout


def create(name, links=[]):
    positions = [.33, 1.]

    publisher, created = Publisher.objects.get_or_create(name=name)
    if created:
        stdout.p([_('Id'), publisher.id], positions=positions)
        stdout.p([_('Name'), publisher.name], positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(Q(pk=url if url.isdigit() else None) | Q(link=url)).get_or_create(defaults={'link':url})
            publisher.links.add(link)
            stdout.p([_('Links') if i == 0 else '', link.link], after=None if has_next else '_', positions=positions)

        publisher.save()
        stdout.p([_('Successfully added publisher "%(name)s" with id "%(id)s".') % {'name':publisher.name, 'id':publisher.id}], after='=', positions=[1.])
    else:
        stdout.p([_('The publisher "%(name)s" already exists with id "%(id)s", aborting...') % {'name':publisher.name, 'id':publisher.id}], after='=', positions=[1.])
    return publisher, created


def edit(publisher, field, value):
    assert field in ['name', '+link', '-link']

    if field == 'name':
        publisher.name = value
    elif field == '+link':
        link, created = Link.objects.filter(Q(pk=value if value.isdigit() else None) | Q(link=value)).get_or_create(defaults={'link':value})
        publisher.links.add(link)
    elif field == '-link':
        try:
            link = Link.objects.get(Q(pk=value if value.isdigit() else None) | Q(link=value))
            publisher.links.remove(link)
        except Link.DoesNotExist:
            stdout.p([_('Link "%(name)s" not found.') % {'name':value}], positions=[1.])
    publisher.save()
    stdout.p([_('Successfully edited publisher "%(name)s" with id "%(id)s".') % {'name':publisher.name, 'id':publisher.id}], positions=[1.])


def info(publisher):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), publisher.id], positions=positions)
    stdout.p([_('Name'), publisher.name], positions=positions)

    if publisher.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(publisher.links.all())):
            stdout.p([_('Links') if i == 0 else '', '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)

    if publisher.editions.count() > 0:
        for (i, edition), has_next in lookahead(enumerate(publisher.editions.all().order_by('published_on'))):
            stdout.p([_('Editions') if i == 0 else '', '%s: %s' % (edition.id, str(edition))], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Editions'), ''], positions=positions)
