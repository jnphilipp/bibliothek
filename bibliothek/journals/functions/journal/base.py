# -*- coding: utf-8 -*-

from journals.models import Journal
from links.models import Link
from utils import lookahead, stdout


def create(name, links=[]):
    positions = [.33, 1.]

    journal, created = Journal.objects.get_or_create(name=name)
    if created:
        stdout.p(['Id', journal.id], positions=positions)
        stdout.p(['Name', journal.name], positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.get_or_create(link=url)
            journal.links.add(link)
            stdout.p(['Links' if i == 0 else '', link.link], after=None if has_next else '_', positions=positions)

        journal.save()
        stdout.p(['Successfully added journal "%s" with id "%s".' % (journal.name, journal.id)], after='=', positions=[1.])
    else:
        stdout.p(['The journal "%s" already exists, aborting...' % journal.name], after='=', positions=[1.])
    return journal, created


def edit(journal, field, value):
    assert field in ['name']

    if field == 'name':
        journal.name = value
    journal.save()
    stdout.p(['Successfully edited journal "%s" with id "%s".' % (journal.name, journal.id)], positions=[1.])


def info(journal):
    positions=[.33, 1.]
    stdout.p(['Field', 'Value'], positions=positions, after='=')
    stdout.p(['Id', journal.id], positions=positions)
    stdout.p(['Name', journal.name], positions=positions)

    if journal.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(journal.links.all())):
            if i == 0:
                stdout.p(['Links', '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p(['Links', ''], positions=positions)

    if journal.papers.count() > 0:
        for (i, paper), has_next in lookahead(enumerate(journal.papers.all())):
            if i == 0:
                stdout.p(['Papers', '%s: %s' % (paper.id, paper.title)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (paper.id, paper.title)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p(['Papers', ''], positions=positions)
