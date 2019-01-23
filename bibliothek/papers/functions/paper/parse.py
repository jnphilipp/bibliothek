# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
#
# This file is part of bibliothek.
#
# bibliothek is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# bibliothek is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with bibliothek.  If not, see <http://www.gnu.org/licenses/>.

import os

from datetime import date
from django.core.files import File as DJFile
from django.utils.translation import ugettext_lazy as _
from files.models import File
from journals.models import Journal
from links.models import Link
from papers.models import Paper
from persons.models import Person
from shelves.models import Acquisition
from utils import lookahead

from .. import bibtex


def from_bibtex(bibtex_file, files=[]):
    papers = bibtex.from_file(bibtex_file)
    if len(papers) != len(files):
        for i in range(len(files), len(papers)):
            files.append(None)

    results = []
    for paper, file in zip(papers, files):
        results += [from_dict(paper,
                              [file, bibtex_file] if file else [bibtex_file])]
    return results


def from_dict(paper_dict, files=[]):
    if paper_dict['title'] and paper_dict['title']:
        paper, created = Paper.objects.get_or_create(title=paper_dict['title'])
        if not created:
            return paper, created, None
        if 'bibtex' in paper_dict and paper_dict['bibtex']:
            paper.bibtex = paper_dict['bibtex']
    else:
        return None, False, None

    if 'authors' in paper_dict and paper_dict['authors']:
        for (i, a), has_next in lookahead(enumerate(paper_dict['authors'])):
            p, c = Person.objects.get_or_create(first_name=a['first_name'],
                                                last_name=a['last_name'])
            paper.authors.add(p)

    if 'journal' in paper_dict and paper_dict['journal']:
        journal, c = Journal.objects.get_or_create(name=paper_dict['journal'])
        paper.journal = journal

    if 'volume' in paper_dict and paper_dict['volume']:
        paper.volume = paper_dict['volume']

    if 'publishing_date' in paper_dict and paper_dict['publishing_date']:
        paper.publishing_date = paper_dict['publishing_date']

    if 'url' in paper_dict and paper_dict['url']:
        link, c = Link.objects.get_or_create(link=paper_dict['url'])
        paper.links.add(link)

    for (i, file), has_next in lookahead(enumerate(files)):
        file_name = os.path.basename(file)
        file_obj = File()
        file_obj.file.save(file_name, DJFile(open(file, 'rb')))
        file_obj.content_object = paper
        file_obj.save()
    paper.save()
    acquisition = Acquisition.objects.create(date=date.today(),
                                             content_object=paper)
    return paper, created, acquisition
