# -*- coding: utf-8 -*-

import os

from django.core.files import File as DJFile
from files.models import File
from journals.models import Journal
from links.models import Link
from papers.models import Paper
from persons.models import Person

from . import bibtex


def from_bibtex(bibtex_file, files=[]):
    papers = bibtex.parse(bibtex_file)
    if len(papers) != len(files):
        for i in range(len(files), len(papers)):
            files.append(None)
    for paper, file in zip(papers, files):
        from_dict(paper, file)


def from_dict(paper_dict, file=None):
    print('=' * 100)

    if paper_dict['title']:
        print('Title: %s"%s"' % (' ' * (91 - len(paper_dict['title'])), paper_dict['title']))
        paper, created = Paper.objects.get_or_create(title=paper_dict['title'])
        paper.bibtex = paper_dict['bibtex']
    else:
        print('No title, aborting:')
        print('=' * 100)
        return
    print('_' * 100)

    paper.authors.clear()
    for i, author in enumerate(paper_dict['authors']):
        if i == 0:
            print('Authors: %s%s' % (' ' * (91 - len(str(author))), author))
        else:
            print('%s%s' % (' ' * (100 - len(str(author))), author))
        person, created = Person.objects.get_or_create(first_name=author['first_name'], last_name=author['last_name'])
        paper.authors.add(person)
    print('_' * 100)

    if paper_dict['journal']:
        print('Journal: %s"%s"' % (' ' * (89 - len(paper_dict['journal'])), paper_dict['journal']))
        journal, created = Journal.objects.get_or_create(name=paper_dict['journal'])
        paper.journal = journal
    else:
        print('Journal:')
    print('_' * 100)

    if paper_dict['published_on']:
        print('Published on: %s"%s"' % (' ' * (84 - len(str(paper_dict['published_on']))), paper_dict['published_on']))
        paper.published_on = paper_dict['published_on']
    else:
        print('Published on:')
    print('_' * 100)

    paper.links.clear()
    if paper_dict['url']:
        print('URL: %s"%s"' % (' ' * (93 - len(paper_dict['url'])), paper_dict['url']))
        link, created = Link.objects.get_or_create(link=paper_dict['url'])
        paper.links.add(link)
    else:
        print('URL:')
    print('_' * 100)

    if file:
        print('File: %s"%s"' % (' ' * (92 - len(file)), file))
        file_name = os.path.basename(file)
        file_obj = File()
        file_obj.file.save(file_name, DJFile(open(file, 'rb')))
        file_obj.content_object = paper
        file_obj.save()
    else:
        print('File:')
    print('=' * 100)
    paper.save()
    print('Successfully added paper "%s" with id "%s".' % (paper.title, paper.id))
