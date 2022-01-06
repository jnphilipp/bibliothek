# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2016-2021 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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

from books.models import Book, Edition
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from io import StringIO
from magazines.models import Issue, Magazine
from papers.models import Paper
from shelves.models import Acquisition, Read


class AcquisitionModelTestCase(TestCase):
    def setUp(self):
        self.paper, created = Paper.from_dict({"title": "Really cool stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(self.paper.pk)

        magazine, created = Magazine.from_dict({"name": "Example"})
        self.assertTrue(created)
        self.assertIsNotNone(magazine.pk)

        self.issue, created = Issue.from_dict({"issue": "1/2021"}, magazine)
        self.assertTrue(created)
        self.assertIsNotNone(self.issue.pk)

        book, created = Book.from_dict({"title": "Example"})
        self.assertTrue(created)
        self.assertIsNotNone(book.pk)

        self.edition, created = Edition.from_dict(
            {"publishing_date": "2021-02-01"}, book
        )
        self.assertTrue(created)
        self.assertIsNotNone(self.edition.pk)

    def test_from_to_dict(self):
        for obj in [self.edition, self.issue, self.paper]:
            acquisition, created = Acquisition.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.pk,
                date=datetime.strptime("2021-01-31", "%Y-%m-%d").date(),
                price=5.2,
            )
            self.assertTrue(created)
            self.assertIsNotNone(acquisition.pk)
            self.assertEquals(
                {"date": "2021-01-31", "price": 5.2}, acquisition.to_dict()
            )
            self.assertEquals(
                (acquisition, False),
                Acquisition.from_dict({"date": "2021-01-31", "price": 5.2}, obj),
            )

            acquisition, created = Acquisition.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.pk,
                date=datetime.strptime("2024-02-29", "%Y-%m-%d").date(),
            )
            self.assertTrue(created)
            self.assertIsNotNone(acquisition.pk)
            self.assertEquals({"date": "2024-02-29", "price": 0}, acquisition.to_dict())
            self.assertEquals(
                (acquisition, False),
                Acquisition.from_dict({"date": "2024-02-29", "price": 0}, obj),
            )

            acquisition, created = Acquisition.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.pk,
                price=3.99,
            )
            self.assertTrue(created)
            self.assertIsNotNone(acquisition.pk)
            self.assertEquals({"date": None, "price": 3.99}, acquisition.to_dict())
            self.assertEquals(
                (acquisition, False),
                Acquisition.from_dict({"date": None, "price": 3.99}, obj),
            )

    def test_edit(self):
        for obj in [self.edition, self.issue, self.paper]:
            acquisition, created = Acquisition.from_dict({"date": "2021-01-01"}, obj)
            self.assertTrue(created)
            self.assertIsNotNone(acquisition.pk)

            self.assertEquals(0, acquisition.price)
            acquisition.edit("price", 4.3)
            self.assertEquals(4.3, acquisition.price)

            self.assertEquals(
                datetime.strptime("2021-01-01", "%Y-%m-%d").date(), acquisition.date
            )
            acquisition.edit("date", datetime.strptime("2021-02-01", "%Y-%m-%d").date())
            self.assertEquals(
                datetime.strptime("2021-02-01", "%Y-%m-%d").date(), acquisition.date
            )

    def test_delete(self):
        for obj in [self.edition, self.issue, self.paper]:
            acquisition, created = Acquisition.from_dict({"date": "2021-01-01"}, obj)
            self.assertTrue(created)
            self.assertIsNotNone(acquisition.pk)

            deleted = acquisition.delete()
            self.assertIsNone(acquisition.pk)
            self.assertEquals((1, {"shelves.Acquisition": 1}), deleted)

    def test_get(self):
        for obj in [self.edition, self.issue, self.paper]:
            acquisition, created = Acquisition.from_dict({"date": "2021-01-01"}, obj)
            self.assertTrue(created)
            self.assertIsNotNone(acquisition.pk)

            if type(obj) == Edition:
                acquisition2 = Acquisition.get(obj.book.title)
            elif type(obj) == Issue:
                acquisition2 = Acquisition.get(f"{obj.magazine.name} {obj.issue}")
            elif type(obj) == Paper:
                acquisition2 = Acquisition.get(obj.title)
            self.assertIsNotNone(acquisition2)
            self.assertEquals(acquisition, acquisition2)

            acquisition2 = Acquisition.get(str(acquisition.pk))
            self.assertIsNotNone(acquisition2)
            self.assertEquals(acquisition, acquisition2)

            if type(obj) == Edition:
                edition, created = Edition.from_dict({"title": "Old stuff"}, obj.book)
                self.assertTrue(created)
                self.assertIsNotNone(edition.id)

                acquisition, created = Acquisition.from_dict(
                    {"date": "2021-01-10", "price": 1.99}, edition
                )
                self.assertTrue(created)
                self.assertIsNotNone(acquisition.pk)

                acquisition2 = Acquisition.get(str(acquisition.pk), editions=edition)
                self.assertIsNotNone(acquisition2)
                self.assertEquals(acquisition, acquisition2)
            elif type(obj) == Issue:
                issue, created = Issue.from_dict({"issue": "2/2021"}, obj.magazine)
                self.assertTrue(created)
                self.assertIsNotNone(issue.id)

                acquisition, created = Acquisition.from_dict(
                    {"date": "2021-01-10", "price": 1.99}, issue
                )
                self.assertTrue(created)
                self.assertIsNotNone(acquisition.pk)

                acquisition2 = Acquisition.get(str(acquisition.pk), issues=issue)
                self.assertIsNotNone(acquisition2)
                self.assertEquals(acquisition, acquisition2)
            elif type(obj) == Paper:
                paper, created = Paper.from_dict({"title": "Old stuff"})
                self.assertTrue(created)
                self.assertIsNotNone(paper.id)

                acquisition, created = Acquisition.from_dict(
                    {"date": "2021-01-10", "price": 1.99}, paper
                )
                self.assertTrue(created)
                self.assertIsNotNone(acquisition.pk)

                acquisition2 = Acquisition.get(str(acquisition.pk), papers=paper)
                self.assertIsNotNone(acquisition2)
                self.assertEquals(acquisition, acquisition2)

    def test_search(self):
        for obj in [self.edition, self.issue, self.paper]:
            acquisition, created = Acquisition.from_dict({"date": "2021-01-01"}, obj)
            self.assertTrue(created)
            self.assertIsNotNone(acquisition.pk)

            acquisition, created = Acquisition.from_dict(
                {"date": "2021-01-10", "price": 10.99}, obj
            )
            self.assertTrue(created)
            self.assertIsNotNone(acquisition.pk)

            acquisition, created = Acquisition.from_dict({"price": 1.99}, obj)
            self.assertTrue(created)
            self.assertIsNotNone(acquisition.pk)

            if type(obj) == Edition:
                edition, created = Edition.from_dict({}, obj.book)
                self.assertTrue(created)
                self.assertIsNotNone(edition.id)

                acquisition, created = Acquisition.from_dict(
                    {"date": "2021-01-10", "price": 1.99}, edition
                )
                self.assertTrue(created)
                self.assertIsNotNone(acquisition.pk)

                self.assertEquals(4, Acquisition.objects.all().count())
                self.assertEquals(4, Acquisition.search("example").count())
                self.assertEquals(1, Acquisition.search("4", editions=edition).count())
            elif type(obj) == Issue:
                issue, created = Issue.from_dict({"issue": "2/2021"}, obj.magazine)
                self.assertTrue(created)
                self.assertIsNotNone(issue.id)

                acquisition, created = Acquisition.from_dict(
                    {"date": "2021-01-10", "price": 1.99}, issue
                )
                self.assertTrue(created)
                self.assertIsNotNone(acquisition.pk)

                self.assertEquals(8, Acquisition.objects.all().count())
                self.assertEquals(8, Acquisition.search("example").count())
                self.assertEquals(1, Acquisition.search("8", issues=issue).count())
            elif type(obj) == Paper:
                paper, created = Paper.from_dict({"title": "Old stuff"})
                self.assertTrue(created)
                self.assertIsNotNone(paper.id)

                acquisition, created = Acquisition.from_dict(
                    {"date": "2021-01-10", "price": 1.99}, paper
                )
                self.assertTrue(created)
                self.assertIsNotNone(acquisition.pk)

                self.assertEquals(12, Acquisition.objects.all().count())
                self.assertEquals(3, Acquisition.search("cool").count())
                self.assertEquals(1, Acquisition.search("12", papers=paper).count())

    def test_print(self):
        acquisition, created = Acquisition.from_dict(
            {"date": "2021-01-01", "price": 1.99}, self.edition
        )
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.pk)

        with StringIO() as cout:
            acquisition.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Obj                              1: Example #1                      "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Date                             2021-01-01                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Price                            1.99                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

        acquisition, created = Acquisition.from_dict(
            {"date": "2021-01-01", "price": 1.99}, self.issue
        )
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.pk)

        with StringIO() as cout:
            acquisition.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               2                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Obj                              1: Example 1/2021                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Date                             2021-01-01                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Price                            1.99                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

        acquisition, created = Acquisition.from_dict(
            {"date": "2021-01-01", "price": 1.99}, self.paper
        )
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.pk)

        with StringIO() as cout:
            acquisition.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               3                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Obj                              1: Really cool stuff               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Date                             2021-01-01                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Price                            1.99                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

    def test_save(self):
        for obj in [self.edition, self.issue, self.paper]:
            acquisition = Acquisition(content_object=obj, date="2021-01-01", price=2.2)
            acquisition.save()
            self.assertIsNotNone(acquisition.pk)

            acquisition = Acquisition(content_object=obj, date="2021-01-01")
            acquisition.save()
            self.assertIsNotNone(acquisition.pk)

            acquisition = Acquisition(content_object=obj, price=3.99)
            acquisition.save()
            self.assertIsNotNone(acquisition.pk)


class ReadModelTestCase(TestCase):
    def setUp(self):
        self.paper, created = Paper.from_dict({"title": "Really cool stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(self.paper.id)

        magazine, created = Magazine.from_dict({"name": "Example"})
        self.assertTrue(created)
        self.assertIsNotNone(magazine.pk)

        self.issue, created = Issue.from_dict({"issue": "1/2021"}, magazine)
        self.assertTrue(created)
        self.assertIsNotNone(self.issue.pk)

        book, created = Book.from_dict({"title": "Example"})
        self.assertTrue(created)
        self.assertIsNotNone(book.pk)

        self.edition, created = Edition.from_dict(
            {"publishing_date": "2021-02-01"}, book
        )
        self.assertTrue(created)
        self.assertIsNotNone(self.edition.pk)

    def test_from_to_dict(self):
        for obj in [self.edition, self.issue, self.paper]:
            read, created = Read.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.pk,
                started=datetime.strptime("2021-01-01", "%Y-%m-%d").date(),
                finished=datetime.strptime("2021-01-10", "%Y-%m-%d").date(),
            )
            self.assertTrue(created)
            self.assertIsNotNone(read.pk)
            self.assertEquals(
                {"started": "2021-01-01", "finished": "2021-01-10"}, read.to_dict()
            )
            self.assertEquals(
                (read, False),
                Read.from_dict(
                    {"started": "2021-01-01", "finished": "2021-01-10"}, obj
                ),
            )

            read, created = Read.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.pk,
                started=datetime.strptime("2021-01-31", "%Y-%m-%d").date(),
            )
            self.assertTrue(created)
            self.assertIsNotNone(read.pk)
            self.assertEquals(
                {"started": "2021-01-31", "finished": None}, read.to_dict()
            )
            self.assertEquals(
                (read, False),
                Read.from_dict({"started": "2021-01-31", "finished": None}, obj),
            )

            read, created = Read.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.pk,
                finished=datetime.strptime("2021-01-16", "%Y-%m-%d").date(),
            )
            self.assertTrue(created)
            self.assertIsNotNone(read.pk)
            self.assertEquals(
                {"started": None, "finished": "2021-01-16"}, read.to_dict()
            )
            self.assertEquals(
                (read, False),
                Read.from_dict({"started": None, "finished": "2021-01-16"}, obj),
            )

    def test_edit(self):
        for obj in [self.edition, self.issue, self.paper]:
            read, created = Read.from_dict({"started": "2021-01-01"}, obj)
            self.assertTrue(created)
            self.assertIsNotNone(read.pk)

            self.assertEquals(None, read.finished)
            read.edit("finished", datetime.strptime("2021-02-01", "%Y-%m-%d").date())
            self.assertEquals(
                datetime.strptime("2021-02-01", "%Y-%m-%d").date(), read.finished
            )

            self.assertEquals(
                datetime.strptime("2021-01-01", "%Y-%m-%d").date(), read.started
            )
            read.edit("started", datetime.strptime("2021-02-10", "%Y-%m-%d").date())
            self.assertEquals(
                datetime.strptime("2021-02-10", "%Y-%m-%d").date(), read.started
            )

    def test_delete(self):
        for obj in [self.edition, self.issue, self.paper]:
            read, created = Read.from_dict({"date": "2021-01-01"}, obj)
            self.assertTrue(created)
            self.assertIsNotNone(read.pk)

            deleted = read.delete()
            self.assertIsNone(read.pk)
            self.assertEquals((1, {"shelves.Read": 1}), deleted)

    def test_get(self):
        for obj in [self.edition, self.issue, self.paper]:
            read, created = Read.from_dict({"finished": "2021-01-01"}, obj)
            self.assertTrue(created)
            self.assertIsNotNone(read.pk)

            if type(obj) == Edition:
                read2 = Read.get(obj.book.title)
            elif type(obj) == Issue:
                read2 = Read.get(f"{obj.magazine.name} {obj.issue}")
            elif type(obj) == Paper:
                read2 = Read.get(obj.title)
            self.assertIsNotNone(read2)
            self.assertEquals(read, read2)

            read2 = read.get(str(read.pk))
            self.assertIsNotNone(read2)
            self.assertEquals(read, read2)

            if type(obj) == Edition:
                edition, created = Edition.from_dict({"title": "Old stuff"}, obj.book)
                self.assertTrue(created)
                self.assertIsNotNone(edition.id)

                read, created = Read.from_dict(
                    {"started": "2021-01-10", "finished": "2021-01-31"}, edition
                )
                self.assertTrue(created)
                self.assertIsNotNone(read.pk)

                read2 = read.get(str(read.pk), editions=edition)
                self.assertIsNotNone(read2)
                self.assertEquals(read, read2)
            elif type(obj) == Issue:
                issue, created = Issue.from_dict({"issue": "2/2021"}, obj.magazine)
                self.assertTrue(created)
                self.assertIsNotNone(issue.id)

                read, created = Read.from_dict(
                    {"started": "2021-01-10", "finished": "2021-01-31"}, issue
                )
                self.assertTrue(created)
                self.assertIsNotNone(read.pk)

                read2 = read.get(str(read.pk), issues=issue)
                self.assertIsNotNone(read2)
                self.assertEquals(read, read2)
            elif type(obj) == Paper:
                paper, created = Paper.from_dict({"title": "Old stuff"})
                self.assertTrue(created)
                self.assertIsNotNone(paper.id)

                read, created = Read.from_dict(
                    {"started": "2021-01-10", "finished": "2021-01-31"}, paper
                )
                self.assertTrue(created)
                self.assertIsNotNone(read.pk)

                read2 = read.get(str(read.pk), papers=paper)
                self.assertIsNotNone(read2)
                self.assertEquals(read, read2)

    def test_search(self):
        for obj in [self.edition, self.issue, self.paper]:
            read, created = Read.from_dict({"started": "2021-01-01"}, obj)
            self.assertTrue(created)
            self.assertIsNotNone(read.pk)

            read, created = Read.from_dict(
                {"date": "2021-01-10", "finished": "2021-04-15"}, obj
            )
            self.assertTrue(created)
            self.assertIsNotNone(read.pk)

            read, created = Read.from_dict({"finished": "2021-03-18"}, obj)
            self.assertTrue(created)
            self.assertIsNotNone(read.pk)

            if type(obj) == Edition:
                edition, created = Edition.from_dict({}, obj.book)
                self.assertTrue(created)
                self.assertIsNotNone(edition.id)

                read, created = Read.from_dict(
                    {"date": "2021-01-10", "finished": "2021-01-31"}, edition
                )
                self.assertTrue(created)
                self.assertIsNotNone(read.pk)

                self.assertEquals(4, Read.objects.all().count())
                self.assertEquals(4, Read.search("example").count())
                self.assertEquals(1, Read.search("4", editions=edition).count())
            elif type(obj) == Issue:
                issue, created = Issue.from_dict({"issue": "2/2021"}, obj.magazine)
                self.assertTrue(created)
                self.assertIsNotNone(issue.id)

                read, created = Read.from_dict(
                    {"date": "2021-01-10", "finished": "2021-01-31"}, issue
                )
                self.assertTrue(created)
                self.assertIsNotNone(read.pk)

                self.assertEquals(8, Read.objects.all().count())
                self.assertEquals(8, Read.search("example").count())
                self.assertEquals(1, Read.search("8", issues=issue).count())
            elif type(obj) == Paper:
                paper, created = Paper.from_dict({"title": "Old stuff"})
                self.assertTrue(created)
                self.assertIsNotNone(paper.id)

                read, created = Read.from_dict(
                    {"date": "2021-01-10", "finished": "2021-01-31"}, paper
                )
                self.assertTrue(created)
                self.assertIsNotNone(read.pk)

                self.assertEquals(12, Read.objects.all().count())
                self.assertEquals(3, Read.search("cool").count())
                self.assertEquals(1, Read.search("12", papers=paper).count())

    def test_print(self):
        read, created = Read.from_dict(
            {"started": "2021-01-01", "finished": "2021-01-31"}, self.edition
        )
        self.assertTrue(created)
        self.assertIsNotNone(read.pk)

        with StringIO() as cout:
            read.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Obj                              1: Example #1                      "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Started                          2021-01-01                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Finished                         2021-01-31                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

        read, created = Read.from_dict(
            {"started": "2021-01-01", "finished": "2021-01-31"}, self.issue
        )
        self.assertTrue(created)
        self.assertIsNotNone(read.pk)

        with StringIO() as cout:
            read.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               2                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Obj                              1: Example 1/2021                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Started                          2021-01-01                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Finished                         2021-01-31                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

        read, created = Read.from_dict(
            {"started": "2021-01-01", "finished": "2021-01-31"}, self.paper
        )
        self.assertTrue(created)
        self.assertIsNotNone(read.pk)

        with StringIO() as cout:
            read.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               3                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Obj                              1: Really cool stuff               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Started                          2021-01-01                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Finished                         2021-01-31                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

    def test_save(self):
        for obj in [self.edition, self.issue, self.paper]:
            read = Read(content_object=obj, started="2021-01-01", finished="2021-01-31")
            read.save()
            self.assertIsNotNone(read.pk)

            read = Read(content_object=obj, started="2021-02-01")
            read.save()
            self.assertIsNotNone(read.pk)

            read = Read(content_object=obj, finished="2021-02-28")
            read.save()
            self.assertIsNotNone(read.pk)
