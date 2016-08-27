# -*- coding: utf-8 -*-

from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext as _
from journals.models import Journal
from papers.models import Paper
from persons.models import Person
from utils import lookahead, stdout


def create(title, authors=[], published_on=None, journal=None, volume=None, links=[]):
    positions = [.33, 1.]

    paper, created = Paper.objects.get_or_create(title=title)
    if created:
        stdout.p([_('Id'), paper.id], positions=positions)
        stdout.p([_('Title'), paper.title], positions=positions)

        if len(authors) > 0:
            for (i, a), has_next in lookahead(enumerate(authors)):
                author, c = Person.objects.annotate(name=Concat('first_name', Value(' '), 'last_name')).filter(Q(pk=a if a.isdigit() else None) | Q(name__icontains=a)).get_or_create(defaults={'first_name':a[:a.rfind(' ')], 'last_name':a[a.rfind(' ') + 1 :]})
                paper.authors.add(author)
                stdout.p([_('Authors') if i == 0 else '', '%s: %s' % (author.id, str(author))], after=None if has_next else '_', positions=positions)
        else:
            stdout.p([_('Authors'), ''], positions=positions)

        if published_on:
            paper.published_on = published_on
            stdout.p([_('Published on'), paper.published_on], positions=positions)
        else:
            stdout.p([_('Published on'), ''], positions=positions)

        if journal:
            paper.journal, c = Journal.objects.filter(Q(pk=journal if journal.isdigit() else None) | Q(name__icontains=journal)).get_or_create(defaults={'name':journal})
            stdout.p([_('Journal'), '%s: %s' % (paper.journal.id, paper.journal.name)], positions=positions)
        else:
            stdout.p([_('Journal'), ''], positions=positions)

        if volume:
            paper.volume = volume
            stdout.p([_('Volume'), paper.volume], positions=positions)
        else:
            stdout.p([_('Volume'), ''], positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(Q(pk=url if url.isdigit() else None) | Q(link=url)).get_or_create(defaults={'link':url})
            paper.links.add(link)
            stdout.p([_('Links') if i == 0 else '', '%s: %s' % (link.id, link.link)], after=None if has_next else '_', positions=positions)

        paper.save()
        stdout.p([_('Successfully added paper "%(title)s" with id "%(id)s".') % {'title':paper.title, 'id':paper.id}], after='=', positions=[1.])
    else:
        stdout.p([_('The paper "%(title)s" already exists with id "%(id)s", aborting...') % {'title':paper.title, 'id':paper.id}], after='=', positions=[1.])
    return paper, created


def edit(paper, field, value):
    assert field in ['title', 'published_on', 'journal', 'volume']

    if field == 'title':
        paper.title = value
    elif field == 'published_on':
        paper.published_on = value
    elif field == 'journal':
        paper.journal, c = Journal.objects.filter(Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)).get_or_create(defaults={'name':value})
    elif field == 'volume':
        paper.volume = value
    paper.save()
    stdout.p([_('Successfully edited paper "%(title)s" with id "%(id)s".') % {'title':paper.title, 'id':paper.id}], positions=[1.])


def info(paper):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), paper.id], positions=positions)
    stdout.p([_('Title'), paper.title], positions=positions)

    if paper.authors.count() > 0:
        for (i, author), has_next in lookahead(enumerate(paper.authors.all())):
            if i == 0:
                stdout.p([_('Authors'), '%s: %s' % (author.id, str(author))], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (author.id, str(author))], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Authors'), ''], positions=positions)

    stdout.p([_('Journal'), '%s: %s' % (paper.journal.id, paper.journal.name) if paper.journal else ''], positions=positions)
    stdout.p([_('Volume'), paper.volume], positions=positions)
    stdout.p([_('Published on'), paper.published_on], positions=positions)

    if paper.languages.count() > 0:
        for (i, language), has_next in lookahead(enumerate(paper.languages.all())):
            if i == 0:
                stdout.p([_('Languages'), language], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', language], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Languages'), ''], positions=positions)

    if paper.files.count() > 0:
        for (i, file), has_next in lookahead(enumerate(paper.files.all())):
            if i == 0:
                stdout.p([_('Files'), '%s: %s' % (file.id, file)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (file.id, file)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Files'), ''], positions=positions)

    if paper.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(paper.links.all())):
            if i == 0:
                stdout.p([_('Links'), '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)

    if paper.acquisitions.count() > 0:
        for (i, acquisition), has_next in lookahead(enumerate(paper.acquisitions.all())):
            if i == 0:
                stdout.p([_('Acquisitions'), '%s: date=%s, price=%0.2f' % (acquisition.id, acquisition.date, acquisition.price)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: date=%s, price=%0.2f' % (acquisition.id, acquisition.date, acquisition.price)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Acquisitions'), ''], positions=positions)

    if paper.reads.count() > 0:
        for (i, read), has_next in lookahead(enumerate(paper.reads.all())):
            if i == 0:
                stdout.p([_('Read'), '%s: date started=%s, date finished=%s' % (read.id, read.started, read.finished)], positions=positions, after='' if has_next else '=')
            else:
                stdout.p(['', '%s: date started=%s, date finished=%s' % (read.id, read.started, read.finished)], positions=positions, after='' if has_next else '=')
    else:
        stdout.p([_('Read'), ''], positions=positions, after='=')
