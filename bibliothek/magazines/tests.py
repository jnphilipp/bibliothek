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

import os

from datetime import datetime
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, TestCase
from files.models import File
from io import StringIO
from links.models import Link
from magazines.models import Magazine, Issue
from pathlib import Path
from tempfile import mkdtemp, NamedTemporaryFile


class MagazineModelTestCase(TestCase):
    def test_from_to_dict(self):
        magazine, created = Magazine.objects.get_or_create(name="Cool")
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)
        self.assertEquals(
            {
                "name": "Cool",
                "feed": None,
                "links": None,
            },
            magazine.to_dict(),
        )
        self.assertEquals((magazine, False), Magazine.from_dict(magazine.to_dict()))
        self.assertEquals((magazine, False), Magazine.from_dict({"name": "Cool"}))

        feed, created = Link.from_dict({"url": "https://example.com/feed"})
        self.assertTrue(created)
        self.assertIsNotNone(feed.id)

        link, created = Link.from_dict({"url": "https://example.com"})
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        magazine, created = Magazine.objects.get_or_create(name="Example", feed=feed)
        magazine.links.add(link)
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)
        self.assertEquals(
            {
                "name": "Example",
                "feed": {"url": "https://example.com/feed"},
                "links": [{"url": "https://example.com"}],
            },
            magazine.to_dict(),
        )
        self.assertEquals((magazine, False), Magazine.from_dict(magazine.to_dict()))

    def test_delete(self):
        magazine, created = Magazine.from_dict({"name": "Cool"})
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        deleted = magazine.delete()
        self.assertIsNone(magazine.id)
        self.assertEquals((1, {"magazines.Magazine": 1}), deleted)

        magazine, created = Magazine.from_dict(
            {
                "name": "Example",
                "feed": {"url": "https://example.com/feed"},
                "links": [{"url": "https://example.com"}],
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        deleted = magazine.delete()
        self.assertIsNone(magazine.id)
        self.assertEquals(
            (
                4,
                {
                    "magazines.Magazine": 1,
                    "magazines.Magazine_links": 1,
                    "links.Link": 2,
                },
            ),
            deleted,
        )

        magazine, created = Magazine.from_dict({"name": "Cool"})
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)
        issue, created = Issue.from_dict({"issue": "1"}, magazine)
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)
        issue, created = Issue.from_dict({"issue": "2"}, magazine)
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        deleted = magazine.delete()
        self.assertIsNone(magazine.id)
        self.assertEquals(
            (
                3,
                {
                    "magazines.Magazine": 1,
                    "magazines.Issue": 2,
                },
            ),
            deleted,
        )

    def test_edit(self):
        magazine, created = Magazine.from_dict({"name": "New"})
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        self.assertIsNone(magazine.feed)
        magazine.edit("feed", "https://example.com")
        self.assertIsNotNone(magazine.feed.id)
        self.assertEquals("https://example.com", magazine.feed.link)

        self.assertEquals(0, magazine.links.count())
        magazine.edit("link", "https://example.org")
        self.assertEquals(1, magazine.links.count())
        self.assertEquals("https://example.org", magazine.links.first().link)

    def test_get(self):
        magazine, created = Magazine.from_dict({"name": "Stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        magazine2 = Magazine.get("stuff")
        self.assertIsNotNone(magazine)
        self.assertEquals(magazine, magazine2)

        magazine2 = Magazine.get(str(magazine.id))
        self.assertIsNotNone(magazine)
        self.assertEquals(magazine, magazine2)

    def test_search(self):
        magazine, created = Magazine.from_dict({"name": "Stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        magazine, created = Magazine.from_dict({"name": "Other stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        magazine, created = Magazine.from_dict({"name": "New"})
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        self.assertEquals(3, Magazine.objects.all().count())
        self.assertEquals(2, Magazine.search("stuff").count())
        self.assertEquals(1, Magazine.search("new").count())

    def test_print(self):
        magazine, created = Magazine.from_dict({"name": "Stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        with StringIO() as cout:
            magazine.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Name                             Stuff                              "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Feed                                                                "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Links                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Issue                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

        magazine, created = Magazine.from_dict(
            {
                "name": "New",
                "feed": {"url": "https://example.com/feed"},
                "links": [{"url": "https://example.com"}],
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(magazine.id)

        with StringIO() as cout:
            magazine.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               2                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Name                             New                                "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Feed                             1: https://example.com/feed        "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Links                            2: https://example.com             "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Issue                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

    def test_save(self):
        magazine = Magazine(name="Green Garden")
        magazine.save()
        self.assertIsNotNone(magazine.id)
        self.assertEquals("green-garden", magazine.slug)

        magazine = Magazine(name="Old Garden")
        magazine.feed, created = Link.from_dict({"url": "https://example.com/feed"})
        magazine.save()
        self.assertIsNotNone(magazine.id)
        self.assertEquals("old-garden", magazine.slug)


@override_settings(MEDIA_ROOT=Path(mkdtemp()))
class IssueModelTestCase(TestCase):
    def setUp(self):
        self.magazine, created = Magazine.from_dict({"name": "Stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(self.magazine.id)

    def test_by_shelf(self):
        issue, created = Issue.from_dict(
            {
                "issue": "1/2021",
            },
            self.magazine,
        )
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issue, created = Issue.from_dict(
            {
                "issue": "2/2021",
                "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
            },
            self.magazine,
        )
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issue, created = Issue.from_dict(
            {
                "issue": "3/2021",
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            },
            self.magazine,
        )
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issue, created = Issue.from_dict(
            {
                "issue": "4/2021",
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            },
            self.magazine,
        )
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issue, created = Issue.from_dict(
            {
                "issue": "5/2021",
                "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            },
            self.magazine,
        )
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        self.assertEquals(2, issue.by_shelf("acquired").count())
        self.assertEquals(3, issue.by_shelf("unacquired").count())
        self.assertEquals(3, issue.by_shelf("read").count())
        self.assertEquals(2, issue.by_shelf("unread").count())

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_from_to_dict(self):
        issue, created = Issue.from_dict({"issue": "1/2021"}, self.magazine)
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)
        self.assertEquals(
            {
                "issue": "1/2021",
                "publishing_date": None,
                "cover": None,
                "languages": None,
                "links": None,
                "files": None,
                "acquisitions": None,
                "reads": None,
            },
            issue.to_dict(),
        )
        self.assertEquals(
            (issue, False), Issue.from_dict(issue.to_dict(), self.magazine)
        )

        issue, created = Issue.from_dict(
            {
                "issue": "2/2021",
                "publishing_date": "2021-02-01",
                "languages": [{"name": "Englisch"}],
                "links": [{"url": "https://example.com"}],
                "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            },
            self.magazine,
        )
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)
        self.assertEquals(
            {
                "issue": "2/2021",
                "publishing_date": "2021-02-01",
                "cover": None,
                "languages": [{"name": "Englisch"}],
                "files": None,
                "links": [{"url": "https://example.com"}],
                "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            },
            issue.to_dict(),
        )
        self.assertEquals(
            (issue, False),
            Issue.from_dict(
                {
                    "issue": "2/2021",
                    "publishing_date": "2021-02-01",
                    "languages": [{"name": "Englisch"}],
                    "links": [{"url": "https://example.com"}],
                    "acquisitions": [{"date": "2021-02-01", "price": 10.0}],
                    "reads": [{"started": "2021-02-01", "finished": "2021-02-28"}],
                },
                self.magazine,
            ),
        )

        with NamedTemporaryFile() as f:
            f.write(b"Lorem ipsum dolorem")

            issue, created = Issue.from_dict(
                {
                    "issue": "3/2021",
                    "publishing_date": "2021-03-01",
                    "languages": [{"name": "Englisch"}],
                    "links": [{"url": "https://example.com"}],
                    "files": [{"path": f.name}],
                    "acquisitions": [{"date": "2021-03-01", "price": 10.0}],
                    "reads": [{"started": "2021-03-01", "finished": "2021-03-31"}],
                },
                self.magazine,
            )
            self.assertTrue(created)
            self.assertIsNotNone(issue.id)
            self.assertEquals(
                {
                    "issue": "3/2021",
                    "publishing_date": "2021-03-01",
                    "cover": None,
                    "languages": [{"name": "Englisch"}],
                    "files": [
                        {
                            "path": os.path.join(
                                settings.MEDIA_ROOT,
                                "magazines",
                                str(self.magazine.pk),
                                str(issue.pk),
                                os.path.basename(f.name),
                            )
                        }
                    ],
                    "links": [{"url": "https://example.com"}],
                    "acquisitions": [{"date": "2021-03-01", "price": 10.0}],
                    "reads": [{"started": "2021-03-01", "finished": "2021-03-31"}],
                },
                issue.to_dict(),
            )

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_delete(self):
        issue, created = Issue.from_dict({"issue": "1-2021"}, self.magazine)
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        deleted = issue.delete()
        self.assertIsNone(issue.id)
        self.assertEquals((1, {"magazines.Issue": 1}), deleted)

        issue, created = Issue.from_dict(
            {
                "issue": "1/2021",
                "publishing_date": "2021-03-01",
                "languages": [{"name": "Englisch"}],
                "links": [{"url": "https://example.com"}],
                "acquisitions": [{"date": "2021-03-01", "price": 10.0}],
                "reads": [{"started": "2021-03-01", "finished": "2021-03-31"}],
            },
            self.magazine,
        )
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        deleted = issue.delete()
        self.assertIsNone(issue.id)
        self.assertEquals(
            (
                6,
                {
                    "magazines.Issue": 1,
                    "links.Link": 1,
                    "magazines.Issue_languages": 1,
                    "magazines.Issue_links": 1,
                    "shelves.Acquisition": 1,
                    "shelves.Read": 1,
                },
            ),
            deleted,
        )

        with NamedTemporaryFile() as f:
            f.write(b"Lorem ipsum dolorem")

            issue, created = Issue.from_dict(
                {
                    "issue": "3/2021",
                    "publishing_date": "2021-03-01",
                    "languages": [{"name": "Englisch"}],
                    "links": [{"url": "https://example.com"}],
                    "files": [{"path": f.name}],
                    "acquisitions": [{"date": "2021-03-01", "price": 10.0}],
                    "reads": [{"started": "2021-03-01", "finished": "2021-03-31"}],
                },
                self.magazine,
            )
            self.assertTrue(created)
            self.assertIsNotNone(issue.id)

            deleted = issue.delete()
            self.assertIsNone(issue.id)
            self.assertEquals(
                (
                    7,
                    {
                        "magazines.Issue": 1,
                        "links.Link": 1,
                        "files.File": 1,
                        "magazines.Issue_languages": 1,
                        "magazines.Issue_links": 1,
                        "shelves.Acquisition": 1,
                        "shelves.Read": 1,
                    },
                ),
                deleted,
            )

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_edit(self):
        issue, created = Issue.from_dict({"issue": "1-2021"}, self.magazine)
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issue.edit("issue", "1/2021")
        self.assertEquals("1/2021", issue.issue)

        self.assertIsNone(issue.publishing_date)
        issue.edit(
            "publishing_date", datetime.strptime("2021-02-01", "%Y-%m-%d").date()
        )
        self.assertEquals(
            datetime.strptime("2021-02-01", "%Y-%m-%d").date(), issue.publishing_date
        )

        self.assertEquals(0, issue.languages.count())
        issue.edit("language", "Deutsch")
        self.assertEquals(1, issue.languages.count())
        self.assertEquals("Deutsch", issue.languages.first().name)

        issue.edit("language", "English")
        self.assertEquals(2, issue.languages.count())
        self.assertEquals("English", issue.languages.last().name)

        issue.edit("language", "Deutsch")
        self.assertEquals(1, issue.languages.count())
        self.assertEquals("English", issue.languages.first().name)

        self.assertEquals(0, issue.links.count())
        issue.edit("link", "http://example.com")
        self.assertEquals(1, issue.links.count())
        self.assertEquals("http://example.com", issue.links.first().link)

        issue.edit("link", "http://example.org")
        self.assertEquals(2, issue.links.count())
        self.assertEquals("http://example.org", issue.links.last().link)

        issue.edit("link", "http://example.com")
        self.assertEquals(1, issue.links.count())
        self.assertEquals("http://example.org", issue.links.first().link)

        with NamedTemporaryFile() as f:
            f.write(b"Lorem ipsum dolorem")

            issue.edit("file", f.name)
            self.assertEquals(1, issue.files.count())
            self.assertEquals(
                {
                    "path": os.path.join(
                        settings.MEDIA_ROOT,
                        "magazines",
                        str(self.magazine.pk),
                        str(issue.pk),
                        os.path.basename(f.name),
                    )
                },
                issue.files.first().to_dict(),
            )

    def test_get(self):
        issue, created = Issue.from_dict(
            {
                "issue": "2/2021",
            },
            self.magazine,
        )
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issue2 = Issue.get("Stuff 2/2021")
        self.assertIsNotNone(issue2)
        self.assertEquals(issue, issue2)

        issue2 = Issue.get(str(issue.id))
        self.assertIsNotNone(issue2)
        self.assertEquals(issue, issue2)

    def test_search(self):
        issue, created = Issue.from_dict(
            {
                "issue": "1/2020",
            },
            self.magazine,
        )
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issue, created = Issue.from_dict(
            {
                "issue": "1/2021",
            },
            self.magazine,
        )
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        issue, created = Issue.from_dict(
            {
                "issue": "2/2021",
            },
            self.magazine,
        )
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        self.assertEquals(3, Issue.objects.all().count())
        self.assertEquals(1, Issue.search("Stuff 2020").count())
        self.assertEquals(2, Issue.search("Stuff 2021").count())

    def test_print(self):
        issue, created = Issue.from_dict(
            {
                "issue": "1/2021",
                "publishing_date": "2021-01-01",
                "languages": [{"name": "Englisch"}],
            },
            self.magazine,
        )
        self.assertTrue(created)
        self.assertIsNotNone(issue.id)

        with StringIO() as cout:
            issue.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Magazine                         1: Stuff                           "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Issue                            1/2021                             "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Publishing date                  2021-01-01                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Cover                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Languages                        1: Englisch                        "
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
                + "Read                                                                "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_save(self):
        issue = Issue(issue="1/2021")
        issue.magazine = self.magazine
        issue.save()
        self.assertIsNotNone(issue.id)

        issue = Issue(issue="2/2021")
        issue.magazine = self.magazine
        issue.publishing_date = datetime.strptime("2021-02-01", "%Y-%m-%d").date()
        issue.save()
        self.assertIsNotNone(issue.id)

        file = File(file=SimpleUploadedFile("test.txt", b"Lorem ipsum dolorem"))
        file.save()
        self.assertIsNotNone(file.id)
        self.assertEquals("files/test.txt", file.file.name)

        issue.files.add(file)
        issue.save()
        self.assertEquals("magazines/1/2/test.txt", issue.files.first().file.name)
