# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2016-2022 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Papers Django app tests."""

import os

from datetime import datetime
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, TestCase
from files.models import File
from io import StringIO
from journals.models import Journal
from languages.models import Language
from links.models import Link
from papers.models import Paper, Proceedings
from pathlib import Path
from persons.models import Person
from shelves.models import Acquisition, Read
from tempfile import mkdtemp, NamedTemporaryFile


PAPERS_BIBTEX = [
    """@ARTICLE{arXiv1706.02515,
  author = {Klambauer, Günter and Unterthiner, Thomas and Mayr, Andreas and Hochreiter, Sepp},
  title = "Self-Normalizing Neural Networks",
  journal = {ArXiv e-prints},
  archivePrefix = "arXiv",
  eprint = {1706.02515},
  primaryClass = "cs.LG",
  keywords = {Computer Science - Learning, Statistics - Machine Learning},
  year = 2017,
  month = "Jun",
  url = {https://arxiv.org/abs/1706.02515},
  adsurl = {http://adsabs.harvard.edu/abs/2017arXiv170602515K},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}""",
    """@ARTICLE{arXiv1805.08671,
  author = {Liang, Shiyu and Sun, Ruoyu and Lee, Jason D. and Srikant, R.},
  title = "Adding One Neuron Can Eliminate All Bad Local Minima",
  journal = {ArXiv e-prints},
  archivePrefix = "arXiv",
  eprint = {1805.08671},
  primaryClass = "stat.ML",
  keywords = {Statistics - Machine Learning, Computer Science - Learning},
  year = 2018,
  month = may,
  url = {https://arxiv.org/abs/1805.08671},
  adsurl = {http://adsabs.harvard.edu/abs/2018arXiv180508671L},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}""",
    """@conference{nlpinai22,
  author={Michael Richter and Maria Bardají I. Farré and Max Kölbl and Yuki Kyogoku and J. Philipp and Tariq Yousef and Gerhard Heyer and Nikolaus Himmelmann},
  title={Uniform Density in Linguistic Information Derived from Dependency Structures},
  booktitle={Proceedings of the 14th International Conference on Agents and Artificial Intelligence - Volume 1: NLPinAI,},
  year={2022},
  pages={496-503},
  publisher={SciTePress},
  organization={INSTICC},
  doi={10.5220/0010969600003116},
  isbn={978-989-758-547-0},
}""",
]

PROCEEDINGS_BIBTEX = [
    """@PROCEEDINGS{icaart2022,
  title = {Proceedings of the 14th International Conference on Agents and Artificial Intelligence},
  booktitle = {Proceedings of the 14th International Conference on Agents and Artificial Intelligence},
  publisher = {SciTePress},
  year = {2022},
  doi = {10.5220/0000155600003116},
  isbn = {978-989-758-395-7}
}""",
    """@PROCEEDINGS{icaart2022,
  title = {Proceedings of the 12th International Conference on Agents and Artificial Intelligence},
  booktitle = {Proceedings of the 12th International Conference on Agents and Artificial Intelligence},
  publisher = {SciTePress},
  year = {2020},
  doi = {10.5220/0000131700002507},
  isbn = {978-989-558-495-6}
}""",
]


class PaperModelTestCase(TestCase):
    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_from_bibfile(self):
        papers = []
        for bibtex in PAPERS_BIBTEX:
            with NamedTemporaryFile() as f:
                f.write(bibtex.encode("utf8"))
                f.flush()

                papers += [(Paper.from_bibfile(f.name)[0], f.name)]
        self.assertEquals(3, len(papers))
        self.assertEquals(
            (
                {
                    "title": "Self-Normalizing Neural Networks",
                    "authors": [
                        {"name": "Andreas Mayr", "links": None},
                        {"name": "Günter Klambauer", "links": None},
                        {"name": "Sepp Hochreiter", "links": None},
                        {"name": "Thomas Unterthiner", "links": None},
                    ],
                    "journal": {"name": "ArXiv e-prints", "links": None},
                    "volume": "1706.02515",
                    "doi": None,
                    "proceedings": None,
                    "publishing_date": "2017-06-01",
                    "publisher": None,
                    "series": None,
                    "languages": None,
                    "files": [
                        {
                            "path": os.path.join(
                                settings.MEDIA_ROOT,
                                "papers",
                                str(papers[0][0][0].pk),
                                os.path.basename(papers[0][1]),
                            )
                        }
                    ],
                    "bibtex": PAPERS_BIBTEX[0],
                    "links": [{"url": "https://arxiv.org/abs/1706.02515"}],
                    "acquisitions": None,
                    "reads": None,
                },
                True,
            ),
            (papers[0][0][0].to_dict(), papers[0][0][1]),
        )
        self.assertEquals(
            (
                {
                    "title": "Adding One Neuron Can Eliminate All Bad Local Minima",
                    "authors": [
                        {"name": "Jason D. Lee", "links": None},
                        {"name": "R. Srikant", "links": None},
                        {"name": "Ruoyu Sun", "links": None},
                        {"name": "Shiyu Liang", "links": None},
                    ],
                    "journal": {"name": "ArXiv e-prints", "links": None},
                    "volume": "1805.08671",
                    "doi": None,
                    "proceedings": None,
                    "publishing_date": "2018-05-01",
                    "publisher": None,
                    "series": None,
                    "languages": None,
                    "files": [
                        {
                            "path": os.path.join(
                                settings.MEDIA_ROOT,
                                "papers",
                                str(papers[1][0][0].pk),
                                os.path.basename(papers[1][1]),
                            )
                        }
                    ],
                    "bibtex": PAPERS_BIBTEX[1],
                    "links": [{"url": "https://arxiv.org/abs/1805.08671"}],
                    "acquisitions": None,
                    "reads": None,
                },
                True,
            ),
            (papers[1][0][0].to_dict(), papers[1][0][1]),
        )
        self.assertEquals(
            (
                {
                    "title": "Uniform Density in Linguistic Information Derived from"
                    + " Dependency Structures",
                    "authors": [
                        {"name": "Gerhard Heyer", "links": None},
                        {"name": "J. Philipp", "links": None},
                        {"name": "Maria Bardají I. Farré", "links": None},
                        {"name": "Max Kölbl", "links": None},
                        {"name": "Michael Richter", "links": None},
                        {"name": "Nikolaus Himmelmann", "links": None},
                        {"name": "Tariq Yousef", "links": None},
                        {"name": "Yuki Kyogoku", "links": None},
                    ],
                    "journal": None,
                    "volume": None,
                    "doi": "10.5220/0010969600003116",
                    "proceedings": None,
                    "publishing_date": "2022-01-01",
                    "publisher": {"name": "SciTePress", "links": None},
                    "series": None,
                    "languages": None,
                    "files": [
                        {
                            "path": os.path.join(
                                settings.MEDIA_ROOT,
                                "papers",
                                str(papers[2][0][0].pk),
                                os.path.basename(papers[2][1]),
                            )
                        }
                    ],
                    "bibtex": PAPERS_BIBTEX[2],
                    "links": None,
                    "acquisitions": None,
                    "reads": None,
                },
                True,
            ),
            (papers[2][0][0].to_dict(), papers[2][0][1]),
        )

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_from_bibtex(self):
        papers = []
        for bibtex in PAPERS_BIBTEX:
            papers += Paper.from_bibtex(bibtex)
        self.assertEquals(3, len(papers))
        self.assertEquals(
            (
                {
                    "title": "Self-Normalizing Neural Networks",
                    "authors": [
                        {"name": "Andreas Mayr", "links": None},
                        {"name": "Günter Klambauer", "links": None},
                        {"name": "Sepp Hochreiter", "links": None},
                        {"name": "Thomas Unterthiner", "links": None},
                    ],
                    "journal": {"name": "ArXiv e-prints", "links": None},
                    "volume": "1706.02515",
                    "doi": None,
                    "proceedings": None,
                    "publisher": None,
                    "series": None,
                    "publishing_date": "2017-06-01",
                    "languages": None,
                    "files": None,
                    "bibtex": PAPERS_BIBTEX[0],
                    "links": [{"url": "https://arxiv.org/abs/1706.02515"}],
                    "acquisitions": None,
                    "reads": None,
                },
                True,
            ),
            (papers[0][0].to_dict(), papers[0][1]),
        )
        self.assertEquals(
            (
                {
                    "title": "Adding One Neuron Can Eliminate All Bad Local Minima",
                    "authors": [
                        {"name": "Jason D. Lee", "links": None},
                        {"name": "R. Srikant", "links": None},
                        {"name": "Ruoyu Sun", "links": None},
                        {"name": "Shiyu Liang", "links": None},
                    ],
                    "journal": {"name": "ArXiv e-prints", "links": None},
                    "volume": "1805.08671",
                    "doi": None,
                    "proceedings": None,
                    "publishing_date": "2018-05-01",
                    "publisher": None,
                    "series": None,
                    "languages": None,
                    "files": None,
                    "bibtex": PAPERS_BIBTEX[1],
                    "links": [{"url": "https://arxiv.org/abs/1805.08671"}],
                    "acquisitions": None,
                    "reads": None,
                },
                True,
            ),
            (papers[1][0].to_dict(), papers[1][1]),
        )
        self.assertEquals(
            (
                {
                    "title": "Uniform Density in Linguistic Information Derived from"
                    + " Dependency Structures",
                    "authors": [
                        {"name": "Gerhard Heyer", "links": None},
                        {"name": "J. Philipp", "links": None},
                        {"name": "Maria Bardají I. Farré", "links": None},
                        {"name": "Max Kölbl", "links": None},
                        {"name": "Michael Richter", "links": None},
                        {"name": "Nikolaus Himmelmann", "links": None},
                        {"name": "Tariq Yousef", "links": None},
                        {"name": "Yuki Kyogoku", "links": None},
                    ],
                    "journal": None,
                    "volume": None,
                    "doi": "10.5220/0010969600003116",
                    "proceedings": None,
                    "publishing_date": "2022-01-01",
                    "publisher": {"name": "SciTePress", "links": None},
                    "series": None,
                    "languages": None,
                    "files": None,
                    "bibtex": PAPERS_BIBTEX[2],
                    "links": None,
                    "acquisitions": None,
                    "reads": None,
                },
                True,
            ),
            (papers[2][0].to_dict(), papers[2][1]),
        )

    def test_by_shelf(self):
        paper, created = Paper.from_dict(
            {
                "title": "Random Science",
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        paper, created = Paper.from_dict(
            {
                "title": "Random Science stuff",
                "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        paper, created = Paper.from_dict(
            {
                "title": "Random new stuff",
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        paper, created = Paper.from_dict(
            {
                "title": "Stuff from Science",
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        paper, created = Paper.from_dict(
            {
                "title": "Science stuff",
                "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        self.assertEquals(2, Paper.by_shelf("acquired").count())
        self.assertEquals(3, Paper.by_shelf("unacquired").count())
        self.assertEquals(3, Paper.by_shelf("read").count())
        self.assertEquals(2, Paper.by_shelf("unread").count())

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_from_to_dict(self):
        author1, created = Person.from_dict({"name": "John Doe"})
        self.assertTrue(created)
        self.assertIsNotNone(author1.id)

        author2, created = Person.from_dict({"name": "Jane Doe"})
        self.assertTrue(created)
        self.assertIsNotNone(author2.id)

        journal, created = Journal.from_dict({"name": "Science Journal"})
        self.assertTrue(created)
        self.assertIsNotNone(journal.id)

        paper, created = Paper.objects.get_or_create(
            title="Random new stuff", journal=journal, volume="1/2021"
        )
        paper.authors.add(author1)
        paper.authors.add(author2)
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)
        self.assertEquals(
            {
                "title": "Random new stuff",
                "authors": [
                    {"name": "Jane Doe", "links": None},
                    {"name": "John Doe", "links": None},
                ],
                "journal": {"name": "Science Journal", "links": None},
                "volume": "1/2021",
                "doi": None,
                "proceedings": None,
                "publisher": None,
                "series": None,
                "publishing_date": None,
                "languages": None,
                "files": None,
                "bibtex": None,
                "links": None,
                "acquisitions": None,
                "reads": None,
            },
            paper.to_dict(),
        )
        self.assertEquals(
            (paper, False),
            Paper.from_dict(
                {
                    "title": "Random new stuff",
                    "authors": [
                        {"name": "Jane Doe", "links": None},
                        {"name": "John Doe", "links": None},
                    ],
                    "journal": {"name": "Science Journal", "links": None},
                    "volume": "1/2021",
                    "doi": None,
                    "publishing_date": None,
                    "languages": None,
                    "files": None,
                    "bibtex": None,
                    "links": None,
                    "acquisitions": None,
                    "reads": None,
                }
            ),
        )
        self.assertEquals(
            (paper, False),
            Paper.from_dict(
                {
                    "title": "Random new stuff",
                    "authors": [
                        {"name": "Jane Doe"},
                        {"name": "John Doe"},
                    ],
                    "journal": {"name": "Science Journal"},
                    "volume": "1/2021",
                }
            ),
        )
        self.assertEquals(
            (paper, False),
            Paper.from_dict(
                {
                    "title": "Random new stuff",
                    "authors": [
                        {"name": "Jane Doe"},
                        {"name": "John Doe"},
                    ],
                    "journal": {"name": "Science Journal"},
                    "volume": "1/2021",
                }
            ),
        )

        language, created = Language.from_dict({"name": "Englisch"})
        self.assertTrue(created)
        self.assertIsNotNone(language.id)

        link, created = Link.from_dict({"url": "https://example.com"})
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        proceedings, created = Proceedings.from_dict(
            {"title": "2nd Proceedings of something"}
        )
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)

        paper, created = Paper.objects.get_or_create(
            title="Random Science stuff",
            publishing_date=datetime.strptime("2021-01-01", "%Y-%m-%d").date(),
            proceedings=proceedings,
            journal=journal,
            volume="2/2021",
            doi="some/doi",
        )
        paper.authors.add(author1)
        paper.authors.add(author2)
        paper.languages.add(language)
        paper.links.add(link)
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        acquisition, created = Acquisition.from_dict(
            {"date": "2021-01-02", "price": 10}, paper
        )
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.id)

        read, created = Read.from_dict(
            {"started": "2021-01-02", "finished": "2021-01-03"}, paper
        )
        self.assertTrue(created)
        self.assertIsNotNone(read.id)
        self.assertEquals(
            {
                "title": "Random Science stuff",
                "authors": [
                    {"name": "Jane Doe", "links": None},
                    {"name": "John Doe", "links": None},
                ],
                "journal": {"name": "Science Journal", "links": None},
                "volume": "2/2021",
                "doi": "some/doi",
                "proceedings": {
                    "title": "2nd Proceedings of something",
                    "editors": None,
                    "publishing_date": None,
                    "isbn": None,
                    "doi": None,
                    "volume": None,
                    "publisher": None,
                    "series": None,
                    "bibtex": None,
                    "languages": None,
                    "files": None,
                    "links": None,
                    "acquisitions": None,
                    "reads": None,
                },
                "publisher": None,
                "series": None,
                "publishing_date": "2021-01-01",
                "languages": [{"name": "Englisch"}],
                "files": None,
                "bibtex": None,
                "links": [{"url": "https://example.com"}],
                "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            },
            paper.to_dict(),
        )
        self.assertEquals(
            (paper, False),
            Paper.from_dict(
                {
                    "title": "Random Science stuff",
                    "authors": [
                        {"name": "Jane Doe", "links": None},
                        {"name": "John Doe", "links": None},
                    ],
                    "journal": {"name": "Science Journal", "links": None},
                    "volume": "2/2021",
                    "doi": "some/doi",
                    "publishing_date": "2021-01-01",
                    "publisher": None,
                    "series": None,
                    "languages": [{"name": "Englisch"}],
                    "files": None,
                    "bibtex": None,
                    "links": [{"url": "https://example.com"}],
                    "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                    "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
                }
            ),
        )
        self.assertEquals(
            (paper, False),
            Paper.from_dict(
                {
                    "title": "Random Science stuff",
                    "authors": [
                        {"name": "Jane Doe"},
                        {"name": "John Doe"},
                    ],
                    "journal": {"name": "Science Journal"},
                    "volume": "2/2021",
                    "doi": "some/doi",
                    "publishing_date": "2021-01-01",
                    "languages": [{"name": "Englisch"}],
                    "links": [{"url": "https://example.com"}],
                    "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                    "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
                }
            ),
        )
        self.assertEquals(
            (paper, False),
            Paper.from_dict(
                {
                    "title": "Random Science stuff",
                    "authors": [
                        {"name": "Jane Doe"},
                        {"name": "John Doe"},
                    ],
                    "journal": {"name": "Science Journal"},
                    "volume": "2/2021",
                    "doi": "some/doi",
                    "publishing_date": "2021-01-01",
                    "languages": [{"name": "Englisch"}],
                    "links": [{"url": "https://example.com"}],
                    "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                    "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
                }
            ),
        )

        with NamedTemporaryFile() as f:
            f.write(b"Lorem ipsum dolorem")

            file, created = File.from_dict({"path": f.name})
            self.assertTrue(created)
            self.assertIsNotNone(file.id)
            self.assertEquals(
                os.path.basename(f.name), os.path.basename(file.file.name)
            )

            paper, created = Paper.objects.get_or_create(
                title="Boring Science stuff",
                publishing_date=datetime.strptime("2021-02-01", "%Y-%m-%d").date(),
                journal=journal,
                volume="2/2021",
            )
            paper.authors.add(author1)
            paper.authors.add(author2)
            paper.languages.add(language)
            paper.links.add(link)
            paper.files.add(file)
            paper.save()
            self.assertTrue(created)
            self.assertIsNotNone(paper.id)
            self.assertEquals(
                {
                    "title": "Boring Science stuff",
                    "authors": [
                        {"name": "Jane Doe", "links": None},
                        {"name": "John Doe", "links": None},
                    ],
                    "journal": {"name": "Science Journal", "links": None},
                    "volume": "2/2021",
                    "doi": None,
                    "proceedings": None,
                    "publisher": None,
                    "series": None,
                    "publishing_date": "2021-02-01",
                    "languages": [{"name": "Englisch"}],
                    "bibtex": None,
                    "links": [{"url": "https://example.com"}],
                    "files": [
                        {
                            "path": os.path.join(
                                settings.MEDIA_ROOT,
                                "papers",
                                str(paper.pk),
                                os.path.basename(f.name),
                            )
                        }
                    ],
                    "acquisitions": None,
                    "reads": None,
                },
                paper.to_dict(),
            )

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_delete(self):
        paper, created = Paper.from_dict({"title": "Paper"})
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        deleted = paper.delete()
        self.assertIsNone(paper.id)
        self.assertEquals((1, {"papers.Paper": 1}), deleted)

        paper, created = Paper.from_dict(
            {"title": "Paper", "links": [{"url": "https://example.com"}]}
        )
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        deleted = paper.delete()
        self.assertIsNone(paper.id)
        self.assertEquals(
            (3, {"papers.Paper": 1, "papers.Paper_links": 1, "links.Link": 1}), deleted
        )

        with NamedTemporaryFile() as f:
            f.write(b"Lorem ipsum dolorem")

            paper, created = Paper.from_dict(
                {
                    "title": "Paper",
                    "links": [{"url": "https://example.com"}],
                    "files": [{"path": f.name}],
                }
            )
            self.assertTrue(created)
            self.assertIsNotNone(paper.id)
            path = os.path.join(
                settings.MEDIA_ROOT, "papers", str(paper.pk), os.path.basename(f.name)
            )
            self.assertEquals({"path": path}, paper.files.first().to_dict())

            deleted = paper.delete()
            self.assertIsNone(paper.id)
            self.assertEquals(
                (
                    4,
                    {
                        "papers.Paper": 1,
                        "papers.Paper_links": 1,
                        "links.Link": 1,
                        "files.File": 1,
                    },
                ),
                deleted,
            )
            self.assertFalse(os.path.exists(path))

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_edit(self):
        paper, created = Paper.from_dict({"title": "Paper 2"})
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        paper.edit("title", "Paper Two")
        self.assertEquals("Paper Two", paper.title)

        self.assertIsNone(paper.journal)
        paper.edit("journal", "Science Journal")
        self.assertIsNotNone(paper.journal.id)
        self.assertEquals("Science Journal", paper.journal.name)

        self.assertIsNone(paper.publisher)
        paper.edit("publisher", "SciTePress")
        self.assertIsNotNone(paper.publisher)
        self.assertEquals("SciTePress", paper.publisher.name)

        self.assertIsNone(paper.series)
        paper.edit("series", "Some series")
        self.assertIsNotNone(paper.series)
        self.assertEquals("Some series", paper.series.name)

        self.assertEquals(0, paper.languages.count())
        paper.edit("language", "Deutsch")
        self.assertEquals(1, paper.languages.count())
        self.assertEquals("Deutsch", paper.languages.first().name)

        paper.edit("language", "English")
        self.assertEquals(2, paper.languages.count())
        self.assertEquals("English", paper.languages.last().name)

        paper.edit("language", "Deutsch")
        self.assertEquals(1, paper.languages.count())
        self.assertEquals("English", paper.languages.first().name)

        self.assertIsNone(paper.publishing_date)
        paper.edit(
            "publishing_date", datetime.strptime("2021-02-01", "%Y-%m-%d").date()
        )
        self.assertEquals(
            datetime.strptime("2021-02-01", "%Y-%m-%d").date(), paper.publishing_date
        )

        with NamedTemporaryFile() as f:
            f.write(b"Lorem ipsum dolorem")

            paper.edit("file", f.name)
            self.assertEquals(1, paper.files.count())
            self.assertEquals(
                {
                    "path": os.path.join(
                        settings.MEDIA_ROOT,
                        "papers",
                        str(paper.pk),
                        os.path.basename(f.name),
                    )
                },
                paper.files.first().to_dict(),
            )

    def test_get(self):
        paper, created = Paper.from_dict({"title": "Boring Science stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        paper2 = Paper.get("boring science")
        self.assertIsNotNone(paper2)
        self.assertEquals(paper, paper2)

        paper2 = Paper.get(str(paper.id))
        self.assertIsNotNone(paper2)
        self.assertEquals(paper, paper2)

    def test_search(self):
        paper, created = Paper.from_dict({"title": "Boring Science stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        paper, created = Paper.from_dict({"title": "Cool Science stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        paper, created = Paper.from_dict({"title": "Weird Science"})
        self.assertTrue(created)
        self.assertIsNotNone(paper.id)

        self.assertEquals(3, Paper.objects.all().count())
        self.assertEquals(2, Paper.search("stuff").count())
        self.assertEquals(3, Paper.search("science").count())

    def test_print(self):
        papers = []
        for bibtex in PAPERS_BIBTEX:
            papers += Paper.from_bibtex(bibtex)
        self.assertEquals(3, len(papers))

        with StringIO() as cout:
            papers[0][0].print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Title                            Self-Normalizing Neural Networks   "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Authors                          3: Andreas Mayr                    "
                + "                                \n                                 1"
                + ": Günter Klambauer                                                \n"
                + "                                 4: Sepp Hochreiter                 "
                + "                                \n                                 2"
                + ": Thomas Unterthiner                                              \n"
                + "____________________________________________________________________"
                + "________________________________\nJournal                          1"
                + ": ArXiv e-prints                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nVolume                           1"
                + "706.02515                                                         \n"
                + "____________________________________________________________________"
                + "________________________________\nDOI                               "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nProceedings                       "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nPublishing date                  2"
                + "017-06-01                                                         \n"
                + "____________________________________________________________________"
                + "________________________________\nPublisher                         "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nSeries                            "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nLanguages                         "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nFiles                             "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nLinks                            1"
                + ": https://arxiv.org/abs/1706.02515                                \n"
                + "____________________________________________________________________"
                + "________________________________\nAcquisitions                      "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nReads                             "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\n",
                cout.getvalue(),
            )

        with StringIO() as cout:
            papers[1][0].print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               2                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Title                            Adding One Neuron Can Eliminate All"
                + " Bad Local Minima               \n__________________________________"
                + "__________________________________________________________________\n"
                + "Authors                          7: Jason D. Lee                    "
                + "                                \n                                 8"
                + ": R. Srikant                                                      \n"
                + "                                 6: Ruoyu Sun                       "
                + "                                \n                                 5"
                + ": Shiyu Liang                                                     \n"
                + "____________________________________________________________________"
                + "________________________________\nJournal                          1"
                + ": ArXiv e-prints                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nVolume                           1"
                + "805.08671                                                         \n"
                + "____________________________________________________________________"
                + "________________________________\nDOI                               "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nProceedings                       "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nPublishing date                  2"
                + "018-05-01                                                         \n"
                + "____________________________________________________________________"
                + "________________________________\nPublisher                         "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nSeries                            "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nLanguages                         "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nFiles                             "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nLinks                            2"
                + ": https://arxiv.org/abs/1805.08671                                \n"
                + "____________________________________________________________________"
                + "________________________________\nAcquisitions                      "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\nReads                             "
                + "                                                                  \n"
                + "____________________________________________________________________"
                + "________________________________\n",
                cout.getvalue(),
            )

        with StringIO() as cout:
            papers[2][0].print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               3                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Title                            Uniform Density in Linguistic Infor"
                + "mation Derived from Dependency  \n                                 S"
                + "tructures                                                         \n"
                + "____________________________________________________________________"
                + "________________________________\nAuthors                          1"
                + "5: Gerhard Heyer                                                  \n"
                + "                                 13: J. Philipp                     "
                + "                                \n                                 1"
                + "0: Maria Bardají I. Farré                                         \n"
                + "                                 11: Max Kölbl                      "
                + "                                \n                                 9"
                + ": Michael Richter                                                 \n"
                + "                                 16: Nikolaus Himmelmann            "
                + "                                \n                                 1"
                + "4: Tariq Yousef                                                   \n"
                + "                                 12: Yuki Kyogoku                   "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Journal                                                             "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Volume                                                              "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "DOI                              10.5220/0010969600003116           "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Proceedings                                                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Publishing date                  2022-01-01                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Publisher                        1: SciTePress                      "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Series                                                              "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Languages                                                           "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Files                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Links                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Acquisitions                                                        "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Reads                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________"
                + "\n",
                cout.getvalue(),
            )

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_save(self):
        paper = Paper(title="Why stuff happens or not?")
        paper.save()
        self.assertIsNotNone(paper.id)
        self.assertEquals("why-stuff-happens-or-not", paper.slug)

        file = File(file=SimpleUploadedFile("test.txt", b"Lorem ipsum dolorem"))
        file.save()
        self.assertIsNotNone(file.id)
        self.assertEquals("files/test.txt", file.file.name)

        paper.files.add(file)
        paper.save()
        self.assertEquals("papers/1/test.txt", paper.files.first().file.name)

        file.refresh_from_db()
        self.assertEquals("papers/1/test.txt", file.file.name)


class ProceedingsModelTestCase(TestCase):
    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_from_bibfile(self):
        proceedings = []
        for bibtex in PROCEEDINGS_BIBTEX:
            with NamedTemporaryFile() as f:
                f.write(bibtex.encode("utf8"))
                f.flush()

                proceedings += [(Proceedings.from_bibfile(f.name)[0], f.name)]
        self.assertEquals(2, len(proceedings))
        self.assertEquals(
            (
                {
                    "title": "Proceedings of the 14th International Conference on Agents and Artificial Intelligence",
                    "editors": None,
                    "volume": None,
                    "series": None,
                    "publisher": {"name": "SciTePress", "links": None},
                    "publishing_date": "2022-01-01",
                    "isbn": "9789897583957",
                    "doi": "10.5220/0000155600003116",
                    "languages": None,
                    "files": [
                        {
                            "path": os.path.join(
                                settings.MEDIA_ROOT,
                                "proceedings",
                                str(proceedings[0][0][0].pk),
                                os.path.basename(proceedings[0][1]),
                            )
                        }
                    ],
                    "bibtex": PROCEEDINGS_BIBTEX[0],
                    "links": None,
                    "acquisitions": None,
                    "reads": None,
                },
                True,
            ),
            (proceedings[0][0][0].to_dict(), proceedings[0][0][1]),
        )
        self.assertEquals(
            (
                {
                    "title": "Proceedings of the 12th International Conference on Agents and Artificial Intelligence",
                    "editors": None,
                    "isbn": "9789895584956",
                    "doi": "10.5220/0000131700002507",
                    "volume": None,
                    "publishing_date": "2020-01-01",
                    "publisher": {"name": "SciTePress", "links": None},
                    "series": None,
                    "languages": None,
                    "files": [
                        {
                            "path": os.path.join(
                                settings.MEDIA_ROOT,
                                "proceedings",
                                str(proceedings[1][0][0].pk),
                                os.path.basename(proceedings[1][1]),
                            )
                        }
                    ],
                    "bibtex": PROCEEDINGS_BIBTEX[1],
                    "links": None,
                    "acquisitions": None,
                    "reads": None,
                },
                True,
            ),
            (proceedings[1][0][0].to_dict(), proceedings[1][0][1]),
        )

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_from_bibtex(self):
        proceedings = []
        for bibtex in PROCEEDINGS_BIBTEX:
            proceedings += Proceedings.from_bibtex(bibtex)
        self.assertEquals(2, len(proceedings))
        self.assertEquals(
            (
                {
                    "title": "Proceedings of the 14th International Conference on Agents and Artificial Intelligence",
                    "editors": None,
                    "volume": None,
                    "series": None,
                    "publisher": {"name": "SciTePress", "links": None},
                    "publishing_date": "2022-01-01",
                    "isbn": "9789897583957",
                    "doi": "10.5220/0000155600003116",
                    "languages": None,
                    "files": None,
                    "bibtex": PROCEEDINGS_BIBTEX[0],
                    "links": None,
                    "acquisitions": None,
                    "reads": None,
                },
                True,
            ),
            (proceedings[0][0].to_dict(), proceedings[0][1]),
        )
        self.assertEquals(
            (
                {
                    "title": "Proceedings of the 12th International Conference on Agents and Artificial Intelligence",
                    "editors": None,
                    "isbn": "9789895584956",
                    "doi": "10.5220/0000131700002507",
                    "volume": None,
                    "publishing_date": "2020-01-01",
                    "publisher": {"name": "SciTePress", "links": None},
                    "series": None,
                    "languages": None,
                    "files": None,
                    "bibtex": PROCEEDINGS_BIBTEX[1],
                    "links": None,
                    "acquisitions": None,
                    "reads": None,
                },
                True,
            ),
            (proceedings[1][0].to_dict(), proceedings[1][1]),
        )

    def test_by_shelf(self):
        proceedings, created = Proceedings.from_dict(
            {
                "title": "1st Proceedings on the International Conference on Something",
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)

        proceedings, created = Proceedings.from_dict(
            {
                "title": "1st Proceedings on the International Conference on Everything",
                "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)

        proceedings, created = Proceedings.from_dict(
            {
                "title": "2nd Proceedings on the International Conference on Something",
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)

        proceedings, created = Proceedings.from_dict(
            {
                "title": "3rd Proceedings on the International Conference on Something",
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)

        proceedings, created = Proceedings.from_dict(
            {
                "title": "2nd Proceedings on the International Conference on Everything",
                "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)

        self.assertEquals(2, Proceedings.by_shelf("acquired").count())
        self.assertEquals(3, Proceedings.by_shelf("unacquired").count())
        self.assertEquals(3, Proceedings.by_shelf("read").count())
        self.assertEquals(2, Proceedings.by_shelf("unread").count())

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_from_to_dict(self):
        editor1, created = Person.from_dict({"name": "John Doe"})
        self.assertTrue(created)
        self.assertIsNotNone(editor1.id)

        editor2, created = Person.from_dict({"name": "Jane Doe"})
        self.assertTrue(created)
        self.assertIsNotNone(editor2.id)

        proceedings, created = Proceedings.objects.get_or_create(
            title="Random new stuff"
        )
        proceedings.editors.add(editor1)
        proceedings.editors.add(editor2)
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)
        self.assertEquals(
            {
                "title": "Random new stuff",
                "editors": [
                    {"name": "Jane Doe", "links": None},
                    {"name": "John Doe", "links": None},
                ],
                "publishing_date": None,
                "isbn": None,
                "doi": None,
                "volume": None,
                "publisher": None,
                "series": None,
                "languages": None,
                "files": None,
                "bibtex": None,
                "links": None,
                "acquisitions": None,
                "reads": None,
            },
            proceedings.to_dict(),
        )
        self.assertEquals(
            (proceedings, False),
            Proceedings.from_dict(
                {
                    "title": "Random new stuff",
                    "editors": [
                        {"name": "Jane Doe", "links": None},
                        {"name": "John Doe", "links": None},
                    ],
                    "publishing_date": None,
                    "isbn": None,
                    "doi": None,
                    "volume": None,
                    "languages": None,
                    "files": None,
                    "bibtex": None,
                    "links": None,
                    "acquisitions": None,
                    "reads": None,
                }
            ),
        )
        self.assertEquals(
            (proceedings, False),
            Proceedings.from_dict(
                {
                    "title": "Random new stuff",
                    "editors": [
                        {"name": "Jane Doe"},
                        {"name": "John Doe"},
                    ],
                }
            ),
        )

        language, created = Language.from_dict({"name": "Englisch"})
        self.assertTrue(created)
        self.assertIsNotNone(language.id)

        link, created = Link.from_dict({"url": "https://example.com"})
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        proceedings, created = Proceedings.objects.get_or_create(
            title="Random Science stuff",
            publishing_date=datetime.strptime("2021-01-01", "%Y-%m-%d").date(),
        )
        proceedings.editors.add(editor1)
        proceedings.editors.add(editor2)
        proceedings.languages.add(language)
        proceedings.links.add(link)
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)

        acquisition, created = Acquisition.from_dict(
            {"date": "2021-01-02", "price": 10}, proceedings
        )
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.id)

        read, created = Read.from_dict(
            {"started": "2021-01-02", "finished": "2021-01-03"}, proceedings
        )
        self.assertTrue(created)
        self.assertIsNotNone(read.id)

        self.assertEquals(
            {
                "title": "Random Science stuff",
                "editors": [
                    {"name": "Jane Doe", "links": None},
                    {"name": "John Doe", "links": None},
                ],
                "publishing_date": "2021-01-01",
                "isbn": None,
                "doi": None,
                "volume": None,
                "publisher": None,
                "series": None,
                "languages": [{"name": "Englisch"}],
                "files": None,
                "bibtex": None,
                "links": [{"url": "https://example.com"}],
                "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            },
            proceedings.to_dict(),
        )
        self.assertEquals(
            (proceedings, False),
            Proceedings.from_dict(
                {
                    "title": "Random Science stuff",
                    "editors": [
                        {"name": "Jane Doe", "links": None},
                        {"name": "John Doe", "links": None},
                    ],
                    "publishing_date": "2021-01-01",
                    "isbn": None,
                    "doi": None,
                    "volume": None,
                    "publisher": None,
                    "series": None,
                    "languages": [{"name": "Englisch"}],
                    "files": None,
                    "bibtex": None,
                    "links": [{"url": "https://example.com"}],
                    "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                    "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
                }
            ),
        )
        self.assertEquals(
            (proceedings, False),
            Proceedings.from_dict(
                {
                    "title": "Random Science stuff",
                    "editors": [
                        {"name": "Jane Doe"},
                        {"name": "John Doe"},
                    ],
                    "publishing_date": "2021-01-01",
                    "isbn": None,
                    "doi": None,
                    "volume": None,
                    "publisher": None,
                    "series": None,
                    "languages": [{"name": "Englisch"}],
                    "links": [{"url": "https://example.com"}],
                    "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                    "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
                }
            ),
        )

        with NamedTemporaryFile() as f:
            f.write(b"Lorem ipsum dolorem")

            file, created = File.from_dict({"path": f.name})
            self.assertTrue(created)
            self.assertIsNotNone(file.id)
            self.assertEquals(
                os.path.basename(f.name), os.path.basename(file.file.name)
            )

            proceedings, created = Proceedings.objects.get_or_create(
                title="Boring Science stuff",
                publishing_date=datetime.strptime("2021-02-01", "%Y-%m-%d").date(),
            )
            proceedings.editors.add(editor1)
            proceedings.editors.add(editor2)
            proceedings.languages.add(language)
            proceedings.links.add(link)
            proceedings.files.add(file)
            proceedings.save()
            self.assertTrue(created)
            self.assertIsNotNone(proceedings.id)
            self.assertEquals(
                {
                    "title": "Boring Science stuff",
                    "editors": [
                        {"name": "Jane Doe", "links": None},
                        {"name": "John Doe", "links": None},
                    ],
                    "publishing_date": "2021-02-01",
                    "isbn": None,
                    "doi": None,
                    "volume": None,
                    "publisher": None,
                    "series": None,
                    "languages": [{"name": "Englisch"}],
                    "bibtex": None,
                    "links": [{"url": "https://example.com"}],
                    "files": [
                        {
                            "path": os.path.join(
                                settings.MEDIA_ROOT,
                                "proceedings",
                                str(proceedings.pk),
                                os.path.basename(f.name),
                            )
                        }
                    ],
                    "acquisitions": None,
                    "reads": None,
                },
                proceedings.to_dict(),
            )

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_delete(self):
        proceedings, created = Proceedings.from_dict({"title": "Proceedings"})
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)

        deleted = proceedings.delete()
        self.assertIsNone(proceedings.id)
        self.assertEquals((1, {"papers.Proceedings": 1}), deleted)

        proceedings, created = Proceedings.from_dict(
            {"title": "Proceedings", "links": [{"url": "https://example.com"}]}
        )
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)

        deleted = proceedings.delete()
        self.assertIsNone(proceedings.id)
        self.assertEquals(
            (
                3,
                {
                    "papers.Proceedings": 1,
                    "papers.Proceedings_links": 1,
                    "links.Link": 1,
                },
            ),
            deleted,
        )

        with NamedTemporaryFile() as f:
            f.write(b"Lorem ipsum dolorem")

            proceedings, created = Proceedings.from_dict(
                {
                    "title": "Proceedings",
                    "links": [{"url": "https://example.com"}],
                    "files": [{"path": f.name}],
                }
            )
            self.assertTrue(created)
            self.assertIsNotNone(proceedings.id)
            path = os.path.join(
                settings.MEDIA_ROOT,
                "proceedings",
                str(proceedings.pk),
                os.path.basename(f.name),
            )
            self.assertEquals({"path": path}, proceedings.files.first().to_dict())

            deleted = proceedings.delete()
            self.assertIsNone(proceedings.id)
            self.assertEquals(
                (
                    4,
                    {
                        "papers.Proceedings": 1,
                        "papers.Proceedings_links": 1,
                        "links.Link": 1,
                        "files.File": 1,
                    },
                ),
                deleted,
            )
            self.assertFalse(os.path.exists(path))

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_edit(self):
        proceedings, created = Proceedings.from_dict({"title": "Some Proceedings"})
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)

        proceedings.edit("title", "Some Proceedings")
        self.assertEquals("Some Proceedings", proceedings.title)

        self.assertIsNone(proceedings.doi)
        proceedings.edit("doi", "haskfhaihhlahlhfalh")
        self.assertEquals("haskfhaihhlahlhfalh", proceedings.doi)

        self.assertIsNone(proceedings.isbn)
        proceedings.edit("isbn", "9889786756543")
        self.assertEquals("9889786756543", proceedings.isbn)

        self.assertIsNone(proceedings.publisher)
        proceedings.edit("publisher", "Science Journal")
        self.assertIsNotNone(proceedings.publisher.id)
        self.assertEquals("Science Journal", proceedings.publisher.name)

        self.assertIsNone(proceedings.series)
        proceedings.edit("series", "Some Science Series")
        self.assertIsNotNone(proceedings.series.id)
        self.assertEquals("Some Science Series", proceedings.series.name)

        self.assertEquals(0, proceedings.languages.count())
        proceedings.edit("language", "Deutsch")
        self.assertEquals(1, proceedings.languages.count())
        self.assertEquals("Deutsch", proceedings.languages.first().name)

        proceedings.edit("language", "English")
        self.assertEquals(2, proceedings.languages.count())
        self.assertEquals("English", proceedings.languages.last().name)

        proceedings.edit("language", "Deutsch")
        self.assertEquals(1, proceedings.languages.count())
        self.assertEquals("English", proceedings.languages.first().name)

        self.assertIsNone(proceedings.publishing_date)
        proceedings.edit(
            "publishing_date", datetime.strptime("2021-02-01", "%Y-%m-%d").date()
        )
        self.assertEquals(
            datetime.strptime("2021-02-01", "%Y-%m-%d").date(),
            proceedings.publishing_date,
        )

        with NamedTemporaryFile() as f:
            f.write(b"Lorem ipsum dolorem")

            proceedings.edit("file", f.name)
            self.assertEquals(1, proceedings.files.count())
            self.assertEquals(
                {
                    "path": os.path.join(
                        settings.MEDIA_ROOT,
                        "proceedings",
                        str(proceedings.pk),
                        os.path.basename(f.name),
                    )
                },
                proceedings.files.first().to_dict(),
            )

    def test_get(self):
        proceedings, created = Proceedings.from_dict({"title": "Boring Science stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)

        proceedings2 = Proceedings.get("boring science")
        self.assertIsNotNone(proceedings2)
        self.assertEquals(proceedings, proceedings2)

        proceedings2 = Proceedings.get(str(proceedings.id))
        self.assertIsNotNone(proceedings2)
        self.assertEquals(proceedings, proceedings2)

    def test_search(self):
        proceedings, created = Proceedings.from_dict({"title": "Boring Science stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)

        proceedings, created = Proceedings.from_dict({"title": "Cool Science stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)

        proceedings, created = Proceedings.from_dict({"title": "Weird Science"})
        self.assertTrue(created)
        self.assertIsNotNone(proceedings.id)

        self.assertEquals(3, Proceedings.objects.all().count())
        self.assertEquals(2, Proceedings.search("stuff").count())
        self.assertEquals(3, Proceedings.search("science").count())

    def test_print(self):
        proceedings = []
        for bibtex in PROCEEDINGS_BIBTEX:
            proceedings += Proceedings.from_bibtex(bibtex)
        self.assertEquals(2, len(proceedings))

        with StringIO() as cout:
            proceedings[0][0].print(cout)
            self.assertEquals(
                "Field                            Value                                "
                + "                              \n===================================="
                + "================================================================\nId"
                + "                               1                                    "
                + "                              \n____________________________________"
                + "________________________________________________________________\nTi"
                + "tle                            Proceedings of the 14th International"
                + " Conference on Agents and     \n                                 Art"
                + "ificial Intelligence                                            \n__"
                + "____________________________________________________________________"
                + "______________________________\nEditors                             "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\nPublishing date                  202"
                + "2-01-01                                                         \n__"
                + "____________________________________________________________________"
                + "______________________________\nISBN                             978"
                + "9897583957                                                      \n__"
                + "____________________________________________________________________"
                + "______________________________\nDOI                              10."
                + "5220/0000155600003116                                           \n__"
                + "____________________________________________________________________"
                + "______________________________\nPublisher                        1: "
                + "SciTePress                                                      \n__"
                + "____________________________________________________________________"
                + "______________________________\nSeries                              "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\nVolume                              "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\nLanguages                           "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\nFiles                               "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\nLinks                               "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\nAcquisitions                        "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\nReads                               "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\n",
                cout.getvalue(),
            )

        with StringIO() as cout:
            proceedings[1][0].print(cout)
            self.assertEquals(
                "Field                            Value                                "
                + "                              \n===================================="
                + "================================================================\nId"
                + "                               2                                    "
                + "                              \n____________________________________"
                + "________________________________________________________________\nTi"
                + "tle                            Proceedings of the 12th International"
                + " Conference on Agents and     \n                                 Art"
                + "ificial Intelligence                                            \n__"
                + "____________________________________________________________________"
                + "______________________________\nEditors                             "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\nPublishing date                  202"
                + "0-01-01                                                         \n__"
                + "____________________________________________________________________"
                + "______________________________\nISBN                             978"
                + "9895584956                                                      \n__"
                + "____________________________________________________________________"
                + "______________________________\nDOI                              10."
                + "5220/0000131700002507                                           \n__"
                + "____________________________________________________________________"
                + "______________________________\nPublisher                        1: "
                + "SciTePress                                                      \n__"
                + "____________________________________________________________________"
                + "______________________________\nSeries                              "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\nVolume                              "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\nLanguages                           "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\nFiles                               "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\nLinks                               "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\nAcquisitions                        "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\nReads                               "
                + "                                                                \n__"
                + "____________________________________________________________________"
                + "______________________________\n",
                cout.getvalue(),
            )

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_save(self):
        proceedings = Proceedings(title="Why stuff happens or not?")
        proceedings.save()
        self.assertIsNotNone(proceedings.id)
        self.assertEquals("why-stuff-happens-or-not", proceedings.slug)

        file = File(file=SimpleUploadedFile("test.txt", b"Lorem ipsum dolorem"))
        file.save()
        self.assertIsNotNone(file.id)
        self.assertEquals("files/test.txt", file.file.name)

        proceedings.files.add(file)
        proceedings.save()
        self.assertEquals("proceedings/1/test.txt", proceedings.files.first().file.name)

        file.refresh_from_db()
        self.assertEquals("proceedings/1/test.txt", file.file.name)
