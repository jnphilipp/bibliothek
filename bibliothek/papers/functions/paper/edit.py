# -*- coding: utf-8 -*-

from papers.models import Paper
from utils import lookahead, stdout

from . import list as paper_list

def cmd(search=None):
    papers = paper_list.by_search(search)

    if papers.count() == 0:
        print('No paper found, aborting...')
    elif papers.count() > 1:
        while True:
            pk = input('> Id: ')
            try:
                paper = papers.get(pk=pk)
                break
            except Paper.DoesNotExist:
                print('Wond Id, try again.')
    else:
        paper = papers[0]

    print('=' * 100)
    print('\n\n')

    while True:
        _print_fields(paper)
        pk = input('> Id: ')
        if pk in ['q', 's', 'save', '10']:
            print('saving paper')


def _print_fields(paper):
    positions=[.05, .33, 1.]
    stdout.p(['Id', 'Field', 'Value'], positions=positions, after='=')
    stdout.p([0, 'Title', paper.title], positions=positions)

    if paper.authors.count() > 0:
        for (i, author), has_next in lookahead(enumerate(paper.authors.all())):
            if i == 0:
                stdout.p([1, 'Authors', str(author)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '', str(author)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([1, 'Authors', ''], positions=positions)

    stdout.p([2, 'Journal', paper.journal.name], positions=positions)
    stdout.p([3, 'Volume', paper.volume], positions=positions)
    stdout.p([4, 'Published on', paper.published_on], positions=positions)

    if paper.languages.count() > 0:
        for (i, language), has_next in lookahead(enumerate(paper.languages.all())):
            if i == 0:
                stdout.p([8, 'Languages', language], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '', language], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([8, 'Languages', ''], positions=positions)

    stdout.p([6, 'Files', ', '.join([str(f) for f in paper.files.all()])], positions=positions)
    stdout.p([7, 'Links', ', '.join([str(l) for l in paper.links.all()])], positions=positions)

    if paper.acquisitions.count() > 0:
        for (i, acquisition), has_next in lookahead(enumerate(paper.acquisitions.all())):
            if i == 0:
                stdout.p([8, 'Acquisitions', acquisition], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '', acquisition], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([8, 'Acquisitions', ''], positions=positions)

    if paper.reads.count() > 0:
        for (i, read), has_next in lookahead(enumerate(paper.reads.all())):
            if i == 0:
                stdout.p([9, 'Read', read], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '', read], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([9, 'Read', ''], positions=positions)

    stdout.p([10, 'Save', ''], positions=positions)
