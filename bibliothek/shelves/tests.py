# -*- coding: utf-8 -*-
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

from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from io import StringIO
from papers.models import Paper
from shelves.models import Acquisition, Read


class AcquisitionModelTestCase(TestCase):
    def setUp(self):
        self.paper, created = Paper.from_dict({"title": "Really cool stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(self.paper.id)

    def test_from_to_dict(self):
        acquisition, created = Acquisition.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(self.paper),
            object_id=self.paper.pk,
            date=datetime.strptime("2021-01-31", "%Y-%m-%d").date(),
            price=5.2,
        )
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.id)
        self.assertEquals({"date": "2021-01-31", "price": 5.2}, acquisition.to_dict())
        self.assertEquals(
            (acquisition, False),
            Acquisition.from_dict({"date": "2021-01-31", "price": 5.2}, self.paper),
        )

        acquisition, created = Acquisition.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(self.paper),
            object_id=self.paper.pk,
            date=datetime.strptime("2024-02-29", "%Y-%m-%d").date(),
        )
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.id)
        self.assertEquals({"date": "2024-02-29", "price": 0}, acquisition.to_dict())
        self.assertEquals(
            (acquisition, False),
            Acquisition.from_dict({"date": "2024-02-29", "price": 0}, self.paper),
        )

        acquisition, created = Acquisition.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(self.paper),
            object_id=self.paper.pk,
            price=3.99,
        )
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.id)
        self.assertEquals({"date": None, "price": 3.99}, acquisition.to_dict())
        self.assertEquals(
            (acquisition, False),
            Acquisition.from_dict({"date": None, "price": 3.99}, self.paper),
        )

    def test_edit(self):
        acquisition, created = Acquisition.from_dict({"date": "2021-01-01"}, self.paper)
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.id)

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
        acquisition, created = Acquisition.from_dict({"date": "2021-01-01"}, self.paper)
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.id)

        deleted = acquisition.delete()
        self.assertIsNone(acquisition.id)
        self.assertEquals((1, {"shelves.Acquisition": 1}), deleted)

    def test_get(self):
        acquisition, created = Acquisition.from_dict({"name": "2021-01-01"}, self.paper)
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.id)

        acquisition2 = Acquisition.get("Really cool stuff")
        self.assertIsNotNone(acquisition2)
        self.assertEquals(acquisition, acquisition2)

        acquisition2 = Acquisition.get("cool")
        self.assertIsNotNone(acquisition2)
        self.assertEquals(acquisition, acquisition2)

        acquisition2 = Acquisition.get(str(acquisition.pk))
        self.assertIsNotNone(acquisition2)
        self.assertEquals(acquisition, acquisition2)

    def test_search(self):
        acquisition, created = Acquisition.from_dict({"date": "2021-01-01"}, self.paper)
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.id)

        acquisition, created = Acquisition.from_dict(
            {"date": "2021-01-10", "price": 10.99}, self.paper
        )
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.id)

        acquisition, created = Acquisition.from_dict({"price": 1.99}, self.paper)
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.id)

        self.assertEquals(3, Acquisition.objects.all().count())
        self.assertEquals(3, Acquisition.search("cool").count())

    def test_print(self):
        acquisition, created = Acquisition.from_dict(
            {"date": "2021-01-01", "price": 1.99}, self.paper
        )
        self.assertTrue(created)
        self.assertIsNotNone(acquisition.id)

        with StringIO() as cout:
            acquisition.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Obj                              Really cool stuff                  "
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
        acquisition = Acquisition(
            content_object=self.paper, date="2021-01-01", price=2.2
        )
        acquisition.save()
        self.assertIsNotNone(acquisition.id)

        acquisition = Acquisition(content_object=self.paper, date="2021-01-01")
        acquisition.save()
        self.assertIsNotNone(acquisition.id)

        acquisition = Acquisition(content_object=self.paper, price=3.99)
        acquisition.save()
        self.assertIsNotNone(acquisition.id)


class ReadModelTestCase(TestCase):
    def setUp(self):
        self.paper, created = Paper.from_dict({"title": "Really cool stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(self.paper.id)

    def test_from_to_dict(self):
        read, created = Read.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(self.paper),
            object_id=self.paper.pk,
            started=datetime.strptime("2021-01-01", "%Y-%m-%d").date(),
            finished=datetime.strptime("2021-01-10", "%Y-%m-%d").date(),
        )
        self.assertTrue(created)
        self.assertIsNotNone(read.id)
        self.assertEquals(
            {"started": "2021-01-01", "finished": "2021-01-10"}, read.to_dict()
        )
        self.assertEquals(
            (read, False),
            Read.from_dict(
                {"started": "2021-01-01", "finished": "2021-01-10"}, self.paper
            ),
        )

        read, created = Read.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(self.paper),
            object_id=self.paper.pk,
            started=datetime.strptime("2021-01-31", "%Y-%m-%d").date(),
        )
        self.assertTrue(created)
        self.assertIsNotNone(read.id)
        self.assertEquals({"started": "2021-01-31", "finished": None}, read.to_dict())
        self.assertEquals(
            (read, False),
            Read.from_dict({"started": "2021-01-31", "finished": None}, self.paper),
        )

        read, created = Read.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(self.paper),
            object_id=self.paper.pk,
            finished=datetime.strptime("2021-01-16", "%Y-%m-%d").date(),
        )
        self.assertTrue(created)
        self.assertIsNotNone(read.id)
        self.assertEquals({"started": None, "finished": "2021-01-16"}, read.to_dict())
        self.assertEquals(
            (read, False),
            Read.from_dict({"started": None, "finished": "2021-01-16"}, self.paper),
        )

    def test_edit(self):
        read, created = Read.from_dict({"started": "2021-01-01"}, self.paper)
        self.assertTrue(created)
        self.assertIsNotNone(read.id)

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
        read, created = Read.from_dict({"date": "2021-01-01"}, self.paper)
        self.assertTrue(created)
        self.assertIsNotNone(read.id)

        deleted = read.delete()
        self.assertIsNone(read.id)
        self.assertEquals((1, {"shelves.Read": 1}), deleted)

    def test_get(self):
        read, created = Read.from_dict({"name": "2021-01-01"}, self.paper)
        self.assertTrue(created)
        self.assertIsNotNone(read.id)

        read2 = Read.get("Really cool stuff")
        self.assertIsNotNone(read2)
        self.assertEquals(read, read2)

        read2 = Read.get("cool")
        self.assertIsNotNone(read2)
        self.assertEquals(read, read2)

        read2 = Read.get(str(read.pk))
        self.assertIsNotNone(read2)
        self.assertEquals(read, read2)

    def test_search(self):
        read, created = Read.from_dict({"started": "2021-01-01"}, self.paper)
        self.assertTrue(created)
        self.assertIsNotNone(read.id)

        read, created = Read.from_dict(
            {"started": "2021-01-10", "finished": "2021-01-31"}, self.paper
        )
        self.assertTrue(created)
        self.assertIsNotNone(read.id)

        read, created = Read.from_dict({"finished": "2021-02-01"}, self.paper)
        self.assertTrue(created)
        self.assertIsNotNone(read.id)

        self.assertEquals(3, Read.objects.all().count())
        self.assertEquals(3, Read.search("cool").count())

    def test_print(self):
        read, created = Read.from_dict(
            {"started": "2021-01-01", "finished": "2021-01-31"}, self.paper
        )
        self.assertTrue(created)
        self.assertIsNotNone(read.id)

        with StringIO() as cout:
            read.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Obj                              Really cool stuff                  "
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
        read = Read(
            content_object=self.paper, started="2021-01-01", finished="2021-01-31"
        )
        read.save()
        self.assertIsNotNone(read.id)

        read = Read(content_object=self.paper, started="2021-02-01")
        read.save()
        self.assertIsNotNone(read.id)

        read = Read(content_object=self.paper, finished="2021-02-28")
        read.save()
        self.assertIsNotNone(read.id)
