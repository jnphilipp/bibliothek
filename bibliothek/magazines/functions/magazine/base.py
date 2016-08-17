# -*- coding: utf-8 -*-

from links.models import Link
from magazines.models import Magazine
from utils import lookahead, stdout


def create(name, feed=None, links=[]):
    positions = [.33, 1.]

    magazine, created = Magazine.objects.get_or_create(name=name.strip())
    if created:
        stdout.p(['Id', magazine.id], positions=positions)
        stdout.p(['Name', magazine.name], positions=positions)

        if feed:
            feed = feed.strip()
            link, c = Link.objects.get_or_create(link=feed)
            magazine.feed = feed
            stdout.p(['Feed', '%s: %s' % (link.id, link.link)], positions=positions)
        else:
            stdout.p(['Feed', ''], positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.get_or_create(link=url.strip())
            magazine.links.add(link)
            stdout.p(['Links' if i == 0 else '', '%s: %s' % (link.id, link.link)], after=None if has_next else '_', positions=positions)
        magazine.save()
        stdout.p(['Successfully added magazine "%s" with id "%s".' % (magazine.name, magazine.id)], after='=', positions=[1.])
    else:
        stdout.p(['The magazine "%s" already exists, aborting...' % name], after='=', positions=[1.])
    return magazine, created


def edit(magazine, field, value):
    assert field in ['name', 'feed']

    if field == 'name':
        magazine.name = value
    elif field == 'feed':
        try:
            link = Link.objects.get(pk=value)
            magazine.feed = link
        except Link.DoesNotExist:
            stdout.p(['Link with id "%s" does not exist.' % value], positions=[1.])
    magazine.save()
    stdout.p(['Successfully edited magazine "%s" with id "%s".' % (magazine.name, magazine.id)], positions=[1.])


def info(magazine):
    positions=[.33, 1.]
    stdout.p(['Field', 'Value'], positions=positions, after='=')
    stdout.p(['Id', magazine.id], positions=positions)
    stdout.p(['Name', magazine.name], positions=positions)
    stdout.p(['Feed', '%s: %s' % (magazine.feed.id, magazine.feed.link) if magazine.feed else ''], positions=positions)

    if magazine.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(magazine.links.all())):
            if i == 0:
                stdout.p(['Links', '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p(['Links', ''], positions=positions)

    if magazine.issues.count() > 0:
        for (i, issue), has_next in lookahead(enumerate(magazine.issues.all().order_by('published_on'))):
            if i == 0:
                stdout.p(['Issue', '%s: %s' % (issue.id, issue.issue)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (issue.id, issue.issue)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p(['Issue', ''], positions=positions)
