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
from papers.models import Paper
from pathlib import Path
from persons.models import Person
from shelves.models import Acquisition, Read
from tempfile import mkdtemp, NamedTemporaryFile


BIBTEX = (
    "@ARTICLE{arXiv1706.02515, author = {Klambauer, Günter and Unterthiner, "
    + 'Thomas and Mayr, Andreas and Hochreiter, Sepp}, title = "Self-Normalizing '
    + 'Neural Networks", journal = {ArXiv e-prints}, archivePrefix = "arXiv", '
    + 'eprint = {1706.02515}, primaryClass = "cs.LG", keywords = {Computer Science '
    + '- Learning, Statistics - Machine Learning}, year = 2017, month = "Jun", url '
    + "= {https://arxiv.org/abs/1706.02515}, adsurl = {http://adsabs.harvard.edu/abs/"
    + "2017arXiv170602515K}, adsnote = {Provided by the SAO/NASA Astrophysics Data "
    + "System}}\n\n@ARTICLE{arXiv1805.08671, author = {Liang, Shiyu and Sun, Ruoyu "
    + 'and Lee, Jason D. and Srikant, R.}, title = "Adding One Neuron Can Eliminate '
    + 'All Bad Local Minima", journal = {ArXiv e-prints}, archivePrefix = "arXiv",'
    + ' eprint = {1805.08671}, primaryClass = "stat.ML", keywords = {Statistics - '
    + "Machine Learning, Computer Science - Learning}, year = 2018, month = may, url "
    + "= {https://arxiv.org/abs/1805.08671}, adsurl = {http://adsabs.harvard.edu/abs/"
    + "2018arXiv180508671L}, adsnote = {Provided by the SAO/NASA Astrophysics Data "
    + "System}}"
)


class PaperModelTestCase(TestCase):
    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_from_bibfile(self):
        papers = None
        with NamedTemporaryFile() as f:
            f.write(BIBTEX.encode("utf8"))
            f.flush()

            papers = Paper.from_bibfile(f.name)
            self.assertEquals(2, len(papers))

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
                    "publishing_date": "2017-06-01",
                    "languages": None,
                    "files": [
                        {
                            "path": os.path.join(
                                settings.MEDIA_ROOT,
                                "papers",
                                str(papers[0][0].pk),
                                os.path.basename(f.name),
                            )
                        }
                    ],
                    "bibtex": '@ARTICLE{arXiv1706.02515, author = {Klambauer, Günter and Unterthiner, Thomas and Mayr, Andreas and Hochreiter, Sepp}, title = "Self-Normalizing Neural Networks", journal = {ArXiv e-prints}, archivePrefix = "arXiv", eprint = {1706.02515}, primaryClass = "cs.LG", keywords = {Computer Science - Learning, Statistics - Machine Learning}, year = 2017, month = "Jun", url = {https://arxiv.org/abs/1706.02515}, adsurl = {http://adsabs.harvard.edu/abs/2017arXiv170602515K}, adsnote = {Provided by the SAO/NASA Astrophysics Data System}}\n\n@ARTICLE{arXiv1805.08671, author = {Liang, Shiyu and Sun, Ruoyu and Lee, Jason D. and Srikant, R.}, title = "Adding One Neuron Can Eliminate All Bad Local Minima", journal = {ArXiv e-prints}, archivePrefix = "arXiv", eprint = {1805.08671}, primaryClass = "stat.ML", keywords = {Statistics - Machine Learning, Computer Science - Learning}, year = 2018, month = may, url = {https://arxiv.org/abs/1805.08671}, adsurl = {http://adsabs.harvard.edu/abs/2018arXiv180508671L}, adsnote = {Provided by the SAO/NASA Astrophysics Data System}}',
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
                    "publishing_date": "2018-05-01",
                    "languages": None,
                    "files": [
                        {
                            "path": os.path.join(
                                settings.MEDIA_ROOT,
                                "papers",
                                str(papers[1][0].pk),
                                os.path.basename(f.name),
                            )
                        }
                    ],
                    "bibtex": '@ARTICLE{arXiv1706.02515, author = {Klambauer, Günter and Unterthiner, Thomas and Mayr, Andreas and Hochreiter, Sepp}, title = "Self-Normalizing Neural Networks", journal = {ArXiv e-prints}, archivePrefix = "arXiv", eprint = {1706.02515}, primaryClass = "cs.LG", keywords = {Computer Science - Learning, Statistics - Machine Learning}, year = 2017, month = "Jun", url = {https://arxiv.org/abs/1706.02515}, adsurl = {http://adsabs.harvard.edu/abs/2017arXiv170602515K}, adsnote = {Provided by the SAO/NASA Astrophysics Data System}}\n\n@ARTICLE{arXiv1805.08671, author = {Liang, Shiyu and Sun, Ruoyu and Lee, Jason D. and Srikant, R.}, title = "Adding One Neuron Can Eliminate All Bad Local Minima", journal = {ArXiv e-prints}, archivePrefix = "arXiv", eprint = {1805.08671}, primaryClass = "stat.ML", keywords = {Statistics - Machine Learning, Computer Science - Learning}, year = 2018, month = may, url = {https://arxiv.org/abs/1805.08671}, adsurl = {http://adsabs.harvard.edu/abs/2018arXiv180508671L}, adsnote = {Provided by the SAO/NASA Astrophysics Data System}}',
                    "links": [{"url": "https://arxiv.org/abs/1805.08671"}],
                    "acquisitions": None,
                    "reads": None,
                },
                True,
            ),
            (papers[1][0].to_dict(), papers[1][1]),
        )

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_from_bibtex(self):
        papers = Paper.from_bibtex(BIBTEX)
        self.assertEquals(2, len(papers))

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
                    "publishing_date": "2017-06-01",
                    "languages": None,
                    "files": None,
                    "bibtex": '@ARTICLE{arXiv1706.02515, author = {Klambauer, Günter and Unterthiner, Thomas and Mayr, Andreas and Hochreiter, Sepp}, title = "Self-Normalizing Neural Networks", journal = {ArXiv e-prints}, archivePrefix = "arXiv", eprint = {1706.02515}, primaryClass = "cs.LG", keywords = {Computer Science - Learning, Statistics - Machine Learning}, year = 2017, month = "Jun", url = {https://arxiv.org/abs/1706.02515}, adsurl = {http://adsabs.harvard.edu/abs/2017arXiv170602515K}, adsnote = {Provided by the SAO/NASA Astrophysics Data System}}\n\n@ARTICLE{arXiv1805.08671, author = {Liang, Shiyu and Sun, Ruoyu and Lee, Jason D. and Srikant, R.}, title = "Adding One Neuron Can Eliminate All Bad Local Minima", journal = {ArXiv e-prints}, archivePrefix = "arXiv", eprint = {1805.08671}, primaryClass = "stat.ML", keywords = {Statistics - Machine Learning, Computer Science - Learning}, year = 2018, month = may, url = {https://arxiv.org/abs/1805.08671}, adsurl = {http://adsabs.harvard.edu/abs/2018arXiv180508671L}, adsnote = {Provided by the SAO/NASA Astrophysics Data System}}',
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
                    "publishing_date": "2018-05-01",
                    "languages": None,
                    "files": None,
                    "bibtex": '@ARTICLE{arXiv1706.02515, author = {Klambauer, Günter and Unterthiner, Thomas and Mayr, Andreas and Hochreiter, Sepp}, title = "Self-Normalizing Neural Networks", journal = {ArXiv e-prints}, archivePrefix = "arXiv", eprint = {1706.02515}, primaryClass = "cs.LG", keywords = {Computer Science - Learning, Statistics - Machine Learning}, year = 2017, month = "Jun", url = {https://arxiv.org/abs/1706.02515}, adsurl = {http://adsabs.harvard.edu/abs/2017arXiv170602515K}, adsnote = {Provided by the SAO/NASA Astrophysics Data System}}\n\n@ARTICLE{arXiv1805.08671, author = {Liang, Shiyu and Sun, Ruoyu and Lee, Jason D. and Srikant, R.}, title = "Adding One Neuron Can Eliminate All Bad Local Minima", journal = {ArXiv e-prints}, archivePrefix = "arXiv", eprint = {1805.08671}, primaryClass = "stat.ML", keywords = {Statistics - Machine Learning, Computer Science - Learning}, year = 2018, month = may, url = {https://arxiv.org/abs/1805.08671}, adsurl = {http://adsabs.harvard.edu/abs/2018arXiv180508671L}, adsnote = {Provided by the SAO/NASA Astrophysics Data System}}',
                    "links": [{"url": "https://arxiv.org/abs/1805.08671"}],
                    "acquisitions": None,
                    "reads": None,
                },
                True,
            ),
            (papers[1][0].to_dict(), papers[1][1]),
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

        paper, created = Paper.objects.get_or_create(
            title="Random Science stuff",
            publishing_date=datetime.strptime("2021-01-01", "%Y-%m-%d").date(),
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
        papers = Paper.from_bibtex(BIBTEX)
        self.assertEquals(2, len(papers))

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
                + "________________________________\nPublishing date                  2"
                + "017-06-01                                                         \n"
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
                + "________________________________\nPublishing date                  2"
                + "018-05-01                                                         \n"
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
