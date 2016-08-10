# -*- coding: utf-8 -*-

import os

from datetime import date
from django.core.files import File as DJFile
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
        stdout.p(['Title', paper_dict['title']], positions=positions)
        paper, created = Paper.objects.get_or_create(title=paper_dict['title'])
        if not created:
            stdout.p(['The paper already exists, aborting...'], after='=')
            return
        else:
            paper.bibtex = paper_dict['bibtex']
    else:
        stdout.p(['No title, aborting...'], after='=')
        return

    for (i, author), has_next in lookahead(enumerate(paper_dict['authors'])):
        if i == 0:
            stdout.p(['Authors', author], after=None if has_next else '_', positions=positions)
        else:
            stdout.p(['', author], after=None if has_next else '_', positions=positions)
        person, created = Person.objects.get_or_create(first_name=author['first_name'], last_name=author['last_name'])
        paper.authors.add(person)

    if paper_dict['journal']:
        stdout.p(['Journal', paper_dict['journal']], positions=positions)
        journal, created = Journal.objects.get_or_create(name=paper_dict['journal'])
        paper.journal = journal

    if paper_dict['volume']:
        stdout.p(['Volume', paper_dict['volume']], positions=positions)
        paper.volume = paper_dict['volume']

    if paper_dict['published_on']:
        stdout.p(['Published on', paper_dict['published_on']], positions=positions)
        paper.published_on = paper_dict['published_on']

    if paper_dict['url']:
        stdout.p(['Links', paper_dict['url']], positions=positions)
        link, created = Link.objects.get_or_create(link=paper_dict['url'])
        paper.links.add(link)

    for (i, file), has_next in lookahead(enumerate(files)):
        stdout.p(['Files' if i == 0 else '', file], after=None if has_next else '_', positions=positions)
        file_name = os.path.basename(file)
        file_obj = File()
        file_obj.file.save(file_name, DJFile(open(file, 'rb')))
        file_obj.content_object = paper
        file_obj.save()
    paper.save()
    stdout.p(['Successfully added paper "%s" with id "%s".' % (paper.title, paper.id)], positions=[1.])
    
    acquisition = Acquisition.objects.create(date=date.today(), content_object=paper)
    stdout.p(['Successfully added acquisition on "%s".' % acquisition.date], after='=', positions=[1.])
