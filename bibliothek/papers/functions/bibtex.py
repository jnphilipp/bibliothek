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

import bibtexparser
import re

from bibtexparser.bparser import BibTexParser
from datetime import datetime


def from_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return parse(f.read())


def parse(bibtex):
    bib_database = BibTexParser(common_strings=True,
                                homogenize_fields=True).parse(bibtex)

    entries = []
    for entry in bib_database.entries:
        title = entry['title'].strip() if 'title' in entry else ''

        authors = []
        entry['author'] = re.sub(r'\s*\n\s*', ' ', entry['author'], flags=re.S)
        for author in re.compile(r'\s+and\s+').split(entry['author']):
            if ',' in author:
                s = author.split(',')
                authors.append({
                    'first_name': s[1].strip(),
                    'last_name': s[0].strip()
                })
            else:
                s = author.rsplit(' ', 1)
                if len(s) == 1:
                    authors.append({
                        'first_name': s[0].strip(),
                        'last_name': None
                    })
                else:
                    authors.append({
                        'first_name': s[0].strip(),
                        'last_name': s[1].strip()
                    })

        journal = entry['journal'].strip() if 'journal' in entry else ''
        volume = entry['volume'].strip() if 'volume' in entry else ''

        if 'number' in entry:
            volume = f'{volume}.{entry["number"]}'

        if 'eprint' in entry and not volume:
            volume = entry['eprint'].strip()
        publisher = entry['publisher'].strip() if 'publisher' in entry else ''

        year = int(entry['year'].strip()) if 'year' in entry else None
        month = entry['month'].strip() if 'month' in entry else None
        if year and month:
            date = datetime.strptime(f'{month} {year}', '%b %Y')
        elif year:
            date = datetime(year, 1, 1)

        if 'timestamp' in entry:
            pub_date = datetime.strptime(entry['timestamp'].strip(),
                                         '%a, %d %b %Y %H:%M:%S %z').date()
        else:
            pub_date = date.date()

        if 'link' in entry:
            url = entry['link'].strip()
        elif 'url' in entry:
            url = entry['url'].strip()
        else:
            url = None

        entries.append({
            'title': title,
            'authors': authors,
            'journal': journal,
            'volume': volume,
            'publisher': publisher,
            'publishing_date': pub_date,
            'url': url,
            'bibtex': bibtex
        })
    return entries
