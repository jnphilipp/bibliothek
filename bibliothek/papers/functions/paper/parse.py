# -*- coding: utf-8 -*-

import os

from datetime import date
from django.core.files import File as DJFile
from django.utils.translation import ugettext as _
from files.models import File
from journals.models import Journal
from links.models import Link
from papers.models import Paper
from persons.models import Person
from shelves.models import Acquisition
from utils import lookahead, stdout

from .. import bibtex


def from_bibtex(bibtex_file, files=[]):
    papers = bibtex.parse(bibtex_file)
    if len(papers) != len(files):
        for i in range(len(files), len(papers)):
            files.append(None)
    for paper, file in zip(papers, files):
        from_dict(paper, [file, bibtex_file] if file else [bibtex_file])
        print()


def from_dict(paper_dict, files=[]):
    positions=[.33, 1.]
    print('=' * 100)

    if paper_dict['title']:
        paper, created = Paper.objects.get_or_create(title=paper_dict['title'])
        stdout.p([_('Title'), paper.title], positions=positions)
        if not created:
            stdout.p([_('The paper "%(title)s" already exists with id "%(id)s", aborting...') % {'title':paper.title, 'id':paper.id}], after='=')
            return paper, created, None
        if 'bibtex' in paper_dict:
            paper.bibtex = paper_dict['bibtex']
    else:
        stdout.p([_('No title given, aborting...')], after='=')
        return None, False, None

    if 'authors' in paper_dict:
        for (i, author), has_next in lookahead(enumerate(paper_dict['authors'])):
            person, c = Person.objects.get_or_create(first_name=author['first_name'], last_name=author['last_name'])
            paper.authors.add(person)
            stdout.p([_('Authors') if i == 0 else '', '%s: %s' % (person.id, str(person))], after=None if has_next else '_', positions=positions)

    if 'journal' in paper_dict:
        journal, c = Journal.objects.get_or_create(name=paper_dict['journal'])
        paper.journal = journal
        stdout.p([_('Journal'), '%s: %s' % (paper.journal.id, paper.journal.name)], positions=positions)

    if 'volume' in paper_dict:
        paper.volume = paper_dict['volume']
        stdout.p([_('Volume'), paper.volume], positions=positions)

    if 'published_on' in paper_dict:
        paper.published_on = paper_dict['published_on']
        stdout.p([_('Published on'), paper.published_on], positions=positions)

    if 'url' in paper_dict:
        link, c = Link.objects.get_or_create(link=paper_dict['url'])
        paper.links.add(link)
        stdout.p([_('Links'), '%s: %s' % (link.id, link.link)], positions=positions)

    for (i, file), has_next in lookahead(enumerate(files)):
        file_name = os.path.basename(file)
        file_obj = File()
        file_obj.file.save(file_name, DJFile(open(file, 'rb')))
        file_obj.content_object = paper
        file_obj.save()
        stdout.p([_('Files') if i == 0 else '', '%s: %s' % (file_obj.id, file_obj)], after=None if has_next else '_', positions=positions)
    paper.save()
    stdout.p([_('Successfully added paper "%(title)s" with id "%(id)s".') % {'title':paper.title, 'id':paper.id}], positions=[1.])

    acquisition = Acquisition.objects.create(date=date.today(), content_object=paper)
    stdout.p([_('Successfully added acquisition on "%(date)s" with id "%(id)s".') % {'date':acquisition.date, 'id':acquisition.id}], after='=', positions=[1.])
    return paper, created, acquisition
