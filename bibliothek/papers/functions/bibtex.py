# -*- coding: utf-8 -*-

import bibtexparser
import re

from datetime import datetime


def parse(bibtex_file):
    with open(bibtex_file, 'r', encoding='utf-8') as f:
        bibtex = f.read()
        bib_database = bibtexparser.loads(bibtex)

    entries = []
    for entry in bib_database.entries:
        title = entry['title'] if 'title' in entry else ''

        authors = []
        for author in re.compile(r'\s+and\s+').split(re.sub(r'(?s)\s*\n\s*', ' ', entry['author'])):
            if ',' in author:
                s = author.split(',')
                authors.append({'first_name':s[1], 'last_name':s[0]})
            else:
                s = author.rsplit(' ', 1)
                authors.append({'first_name':s[0], 'last_name':s[1]})

        journal = entry['journal'] if 'journal' in entry else ''
        volume = entry['volume'] if 'volume' in entry else ''
        volume = '%s.%s' % (volume, entry['number']) if 'number' in entry else volume
        if 'eprint' in entry and not volume:
            volume = entry['eprint']
        publisher = entry['publisher'] if 'publisher' in entry else ''

        year = int(entry['year']) if 'year' in entry else None
        month = entry['month'] if 'month' in entry else None
        if year and month:
            date = datetime.strptime('%s %s' % (month, year), '%b %Y')
        elif year:
            date = datetime(year, 1, 1)

        published_on = datetime.strptime(entry['timestamp'], '%a, %d %b %Y %H:%M:%S %z').date() if 'timestamp' in entry else date.date()
        url = entry['link'] if 'link' in entry else ''

        entries.append({'title':title, 'authors':authors, 'journal':journal, 'volume':volume, 'publisher':publisher, 'published_on':published_on, 'url':url, 'bibtex':bibtex})
    return entries
