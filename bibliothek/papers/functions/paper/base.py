# -*- coding: utf-8 -*-

from journals.models import Journal
from papers.models import Paper
from utils import lookahead, stdout


def create(title, published_on=None, journal_id=None, volume=None):
    positions = [.33, 1.]

    paper, created = Paper.objects.get_or_create(title=title)
    if created:
        stdout.p(['Title', paper.title], positions=positions)

        if published_on:
            paper.published_on = published_on
            stdout.p(['Published on', paper.published_on], positions=positions)
        else:
            stdout.p(['Published on', ''], positions=positions)

        if journal_id:
            try:
                journal = Journal.objects.get(pk=journal_id)
                paper.journal = journal
                stdout.p(['Journal', paper.journal.name], positions=positions)
            except Journal.DoesNotExist:
                stdout.p(['Journal', 'Journal with id "%s" does not exist.' % paper.journal.id], positions=positions)
        else:
            stdout.p(['Journal', ''], positions=positions)

        if volume:
            paper.volume = volume
            stdout.p(['Volume', paper.volume], positions=positions)
        else:
            stdout.p(['Volume', ''], positions=positions)

        paper.save()
        stdout.p(['Successfully added paper "%s" with id "%s".' % (paper.title, paper.id)], after='=', positions=[1.])
    else:
        stdout.p(['The paper "%s" already exists, aborting...' % paper.title], after='=', positions=[1.])
    return paper, created


def edit(paper, field, value):
    assert field in ['title', 'published_on', 'volume']

    if field == 'title':
        paper.title = value
    elif field == 'published_on':
        paper.published_on = value
    elif field == 'journal':
        try:
            journal = Journal.objects.get(pk=value)
            paper.journal = journal
        except Journal.DoesNotExist:
            stdout.p(['Journal with id "%s" does not exist.' % value], positions=[1.])
    elif field == 'volume':
        paper.volume = value
    paper.save()
    stdout.p(['Successfully edited paper "%s" with id "%s".' % (paper.title, paper.id)], positions=[1.])


def info(paper):
    positions=[.33, 1.]
    stdout.p(['Field', 'Value'], positions=positions, after='=')
    stdout.p(['Id', paper.id], positions=positions)
    stdout.p(['Title', paper.title], positions=positions)

    if paper.authors.count() > 0:
        for (i, author), has_next in lookahead(enumerate(paper.authors.all())):
            if i == 0:
                stdout.p(['Authors', '%s: %s' % (author.id, str(author))], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (author.id, str(author))], positions=positions, after='' if has_next else '_')
    else:
        stdout.p(['Authors', ''], positions=positions)

    stdout.p(['Journal', '%s: %s' % (paper.journal.id, paper.journal.name)], positions=positions)
    stdout.p(['Volume', paper.volume], positions=positions)
    stdout.p(['Published on', paper.published_on], positions=positions)

    if paper.languages.count() > 0:
        for (i, language), has_next in lookahead(enumerate(paper.languages.all())):
            if i == 0:
                stdout.p(['Languages', language], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', language], positions=positions, after='' if has_next else '_')
    else:
        stdout.p(['Languages', ''], positions=positions)

    if paper.files.count() > 0:
        for (i, file), has_next in lookahead(enumerate(paper.files.all())):
            if i == 0:
                stdout.p(['Files', '%s: %s' % (file.id, file)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (file.id, file)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p(['Files', ''], positions=positions)

    if paper.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(paper.links.all())):
            if i == 0:
                stdout.p(['Links', '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p(['Links', ''], positions=positions)

    if paper.acquisitions.count() > 0:
        for (i, acquisition), has_next in lookahead(enumerate(paper.acquisitions.all())):
            if i == 0:
                stdout.p(['Acquisitions', '%s: date=%s, price=%0.2f' % (acquisition.id, acquisition.date, acquisition.price)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: date=%s, price=%0.2f' % (acquisition.id, acquisition.date, acquisition.price)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p(['Acquisitions', ''], positions=positions)

    if paper.reads.count() > 0:
        for (i, read), has_next in lookahead(enumerate(paper.reads.all())):
            if i == 0:
                stdout.p(['Read', '%s: date started=%s, date finished=%s' % (read.id, read.started, read.finished)], positions=positions, after='' if has_next else '=')
            else:
                stdout.p(['', '%s: date started=%s, date finished=%s' % (read.id, read.started, read.finished)], positions=positions, after='' if has_next else '=')
    else:
        stdout.p(['Read', ''], positions=positions, after='=')
