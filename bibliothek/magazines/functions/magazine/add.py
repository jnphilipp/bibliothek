# -*- coding: utf-8 -*-

from links.models import Link
from magazines.models import Magazine
from utils import lookahead, stdout


def create(name, feed=None, links=[]):
    positions = [.33, 1.]

    magazine, created = Magazine.objects.get_or_create(name=name.strip())
    if created:
        stdout.p(['Name', name], positions=positions)

        if feed:
            feed = feed.strip()
            link, created = Link.objects.get_or_create(link=feed)
            stdout.p(['Feed', feed], positions=positions)
        else:
            stdout.p(['Feed', ''], positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, created = Link.objects.get_or_create(link=url.strip())
            magazine.links.add(link)
            stdout.p(['Links' if i == 0 else '', link.link], after=None if has_next else '_', positions=positions)
        magazine.save()
        stdout.p(['Successfully added magazine "%s" with id "%s".' % (magazine.name, magazine.id)], after='=', positions=[1.])
    else:
        stdout.p(['The magazine "%s" already exists, aborting...' % name], after='=', positions=[1.])
