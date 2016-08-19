# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from links.models import Link
from persons.models import Person
from utils import lookahead, stdout


def create(first_name, last_name, links=[]):
    positions = [.33, 1.]

    person, created = Person.objects.get_or_create(first_name=first_name, last_name=last_name)
    if created:
        stdout.p([_('Id'), person.id], positions=positions)
        stdout.p([_('First name'), person.first_name], positions=positions)
        stdout.p([_('Last name'), person.last_name], positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.get_or_create(link=url)
            person.links.add(link)
            stdout.p([_('Links') if i == 0 else '', link.link], after=None if has_next else '_', positions=positions)

        person.save()
        stdout.p([_('Successfully added person "%(first_name)s %(last_name)s" with id "%(id)s".') % {'first_name':person.first_name, 'last_name':person.last_name, 'id':person.id}], after='=', positions=[1.])
    else:
        stdout.p([_('The person "%(first_name)s %(last_name)s" already exists with id "%(id)s", aborting...') % {'first_name':person.first_name, 'last_name':person.last_name, 'id':person.id}], after='=', positions=[1.])
    return person, created


def edit(person, field, value):
    assert field in ['first_name', 'last_name']

    if field == 'first_name':
        person.first_name = value
    elif field == 'last_name':
        person.last_name = value
    person.save()
    stdout.p([_('Successfully edited person "%(first_name)s %(last_name)s" with id "%(id)s".') % {'first_name':person.first_name, 'last_name':person.last_name, 'id':person.id}], positions=[1.])


def info(person):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), person.id], positions=positions)
    stdout.p([_('First name'), person.first_name], positions=positions)
    stdout.p([_('Last name'), person.last_name], positions=positions)

    if person.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(publisher.links.all())):
            if i == 0:
                stdout.p([_('Links'), '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)
