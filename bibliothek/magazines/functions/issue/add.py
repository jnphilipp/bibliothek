# -*- coding: utf-8 -*-

import os

from django.core.files import File as DJFile
from files.models import File
from links.models import Link
from magazines.models import Issue
from utils import lookahead, stdout


def create(magazine, issue_name, published_on=None, cover_image=None, links=[], files=[]):
    positions = [.33, 1.]

    issue, created = Issue.objects.get_or_create(magazine=magazine, issue=issue_name.strip())
    if created:
        stdout.p(['issue', issue], positions=positions)

        if published_on:
            issue.published_on = published_on
            stdout.p(['Published on', published_on], positions=positions)
        else:
            stdout.p(['Published on', ''], positions=positions)

        if cover_image:
            issue.cover_image = cover_image
            stdout.p(['Cover image', cover_image], positions=positions)
        else:
            stdout.p(['Cover image', ''], positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, created = Link.objects.get_or_create(link=url.strip())
            issue.links.add(link)
            stdout.p(['Links' if i == 0 else '', link.link], after=None if has_next else '_', positions=positions)

        for (i, file), has_next in lookahead(enumerate(files)):
            file_name = os.path.basename(file)
            file_obj = File()
            file_obj.file.save(file_name, DJFile(open(file, 'rb')))
            file_obj.content_object = issue
            file_obj.save()
            stdout.p(['Files' if i == 0 else '', file_name], after=None if has_next else '_', positions=positions)
        issue.save()
        stdout.p(['Successfully added issue "%s" with id "%s".' % (issue.issue, issue.id)], after='=', positions=[1.])
    else:
        stdout.p(['The issue "%s" already exists, aborting...' % issue_name], after='=', positions=[1.])
