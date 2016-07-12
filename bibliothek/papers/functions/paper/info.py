# -*- coding: utf-8 -*-

from papers.models import Paper
from utils import lookahead, stdout

from . import list as paper_list

def show(search=None):
    papers = paper_list.by_search(search)
    print('=' * 100)
    print('\n\n')

    if papers.count() == 0:
        print('No paper found.')
        print('=' * 100)
        return
    for paper, has_next in lookahead(papers):
        _print_fields(paper)
        if has_next:
            print('\n\n')


def _print_fields(paper):
    positions=[.33, 1.]
    stdout.p(['Field', 'Value'], positions=positions, after='=')
    stdout.p(['Title', paper.title], positions=positions)

    if paper.authors.count() > 0:
        for (i, author), has_next in lookahead(enumerate(paper.authors.all())):
            if i == 0:
                stdout.p(['Authors', str(author)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', str(author)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p(['Authors', ''], positions=positions)

    stdout.p(['Journal', paper.journal.name], positions=positions)
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

    stdout.p(['Files', ', '.join([str(f) for f in paper.files.all()])], positions=positions)
    stdout.p(['Links', ', '.join([str(l) for l in paper.links.all()])], positions=positions)

    if paper.acquisitions.count() > 0:
        for (i, acquisition), has_next in lookahead(enumerate(paper.acquisitions.all())):
            if i == 0:
                stdout.p(['Acquisitions', 'id: %s, date: %s, price: %0.2f' % (acquisition.id, acquisition.date, acquisition.price)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', 'id: %s, date: %s, price: %0.2f' % (acquisition.id, acquisition.date, acquisition.price)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p(['Acquisitions', ''], positions=positions)

    if paper.reads.count() > 0:
        for (i, read), has_next in lookahead(enumerate(paper.reads.all())):
            if i == 0:
                stdout.p(['Read', 'id: %s, date started: %s, date finished: %s' % (read.id, read.started, read.finished)], positions=positions, after='' if has_next else '=')
            else:
                stdout.p(['', 'id: %s, date started: %s, date finished: %s' % (read.id, read.started, read.finished)], positions=positions, after='' if has_next else '=')
    else:
        stdout.p(['Read', ''], positions=positions, after='=')
