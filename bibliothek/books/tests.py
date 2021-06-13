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

import os

from datetime import datetime
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, TestCase
from files.models import File
from genres.models import Genre
from io import StringIO
from links.models import Link
from pathlib import Path
from persons.models import Person
from series.models import Series
from tempfile import mkdtemp, NamedTemporaryFile

from .models import Book, Edition


class BookModelTestCase(TestCase):
    def test_from_to_dict(self):
        book, created = Book.objects.get_or_create(title="Cool")
        self.assertTrue(created)
        self.assertIsNotNone(book.id)
        self.assertEquals(
            {
                "title": "Cool",
                "authors": None,
                "series": None,
                "volume": 0,
                "genres": None,
                "links": None,
            },
            book.to_dict(),
        )
        self.assertEquals((book, False), Book.from_dict(book.to_dict()))
        self.assertEquals((book, False), Book.from_dict({"title": "Cool"}))

        author, created = Person.from_dict({"name": "Max Mustermann"})
        self.assertTrue(created)
        self.assertIsNotNone(author.id)

        series, created = Series.from_dict({"name": "Secret Files"})
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        genre, created = Genre.from_dict({"name": "Fiction"})
        self.assertTrue(created)
        self.assertIsNotNone(genre.id)

        link, created = Link.from_dict({"url": "https://example.com"})
        self.assertTrue(created)
        self.assertIsNotNone(link.id)

        book, created = Book.objects.get_or_create(
            title="Example", series=series, volume=1
        )
        book.authors.add(author)
        book.genres.add(genre)
        book.links.add(link)
        self.assertTrue(created)
        self.assertIsNotNone(book.id)
        self.assertEquals(
            {
                "title": "Example",
                "authors": [{"name": "Max Mustermann", "links": None}],
                "series": {"name": "Secret Files", "links": None},
                "volume": 1,
                "genres": [{"name": "Fiction"}],
                "links": [{"url": "https://example.com"}],
            },
            book.to_dict(),
        )
        self.assertEquals((book, False), Book.from_dict(book.to_dict()))

    def test_delete(self):
        book, created = Book.from_dict({"title": "Cool"})
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        deleted = book.delete()
        self.assertIsNone(book.id)
        self.assertEquals((1, {"books.Book": 1}), deleted)

        book, created = Book.from_dict(
            {
                "title": "Example",
                "authors": [{"name": "Max Mustermann", "links": None}],
                "series": {"name": "Secret Files", "links": None},
                "volume": 1,
                "genres": [{"name": "Fiction"}],
                "links": [{"url": "https://example.com"}],
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(book.id)
        edition, created = Edition.from_dict({"alternate_title": "Eeksempel"}, book)
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)

        deleted = book.delete()
        self.assertIsNone(book.id)
        self.assertEquals(
            (
                8,
                {
                    "books.Book": 1,
                    "books.Book_authors": 1,
                    "books.Book_genres": 1,
                    "books.Book_links": 1,
                    "books.Edition": 1,
                    "genres.Genre": 1,
                    "links.Link": 1,
                    "series.Series": 1,
                },
            ),
            deleted,
        )

    def test_edit(self):
        series, created = Series.from_dict({"name": "Test Series"})
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        person, created = Person.from_dict({"name": "John Do"})
        self.assertTrue(created)
        self.assertIsNotNone(person.id)

        book, created = Book.from_dict(
            {
                "title": "Test2 Book",
                "authors": [person.to_dict()],
                "series": series.to_dict(),
                "volume": 1.0,
                "genres": [{"name": "Romance"}],
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(book.id)
        self.assertEquals(series, book.series)
        self.assertEquals(person, book.authors.first())

        book.edit("title", "IEEE Test Book")
        self.assertEquals("IEEE Test Book", book.title)

        book.edit("author", "Jane Do")
        self.assertEquals(2, book.authors.count())
        self.assertEquals("Jane Do", str(book.authors.all()[0]))
        self.assertEquals("John Do", str(book.authors.all()[1]))

        book.edit("author", str(person.id))
        self.assertEquals(1, book.authors.count())
        self.assertEquals("Jane Do", str(book.authors.all()[0]))

        series, created = Series.from_dict({"name": "Space Series"})
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        book.edit("series", str(series.id))
        self.assertEquals(series, book.series)

        book.edit("volume", 0.75)
        self.assertEquals(0.75, book.volume)

        series, created = Series.from_dict({"name": "Deep Space Series"})
        self.assertTrue(created)
        self.assertIsNotNone(series.id)

        book.edit("series", "Deep Space")
        self.assertEquals(series, book.series)

        book.edit("genre", "SciFi")
        self.assertEquals(2, book.genres.count())
        self.assertEquals("Romance", book.genres.first().name)
        self.assertEquals("SciFi", book.genres.last().name)

        book.edit("genre", "1")
        self.assertEquals(1, book.genres.count())
        self.assertEquals("SciFi", book.genres.first().name)

        book.edit("link", "https://deep.space")
        self.assertEquals(1, book.links.count())
        self.assertEquals("https://deep.space", book.links.first().link)

        book.edit("link", "https://janedo.com/test2book")
        self.assertEquals(2, book.links.count())
        self.assertEquals("https://janedo.com/test2book", book.links.last().link)

        book.edit("link", "https://deep.space")
        self.assertEquals(1, book.links.count())
        self.assertEquals("https://janedo.com/test2book", book.links.first().link)

    def test_get(self):
        book, created = Book.from_dict({"title": "Test Book"})
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        book2 = Book.get("Test Book")
        self.assertIsNotNone(book2)
        self.assertEquals(book, book2)

        book2 = Book.get(str(book.id))
        self.assertIsNotNone(book2)
        self.assertEquals(book, book2)

    def test_search(self):
        book, created = Book.from_dict({"title": "About Stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        book, created = Book.from_dict({"title": "Not so cool Stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        book, created = Book.from_dict({"title": "About cool Stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        self.assertEquals(3, Book.objects.all().count())
        self.assertEquals(3, Book.search("stuff").count())
        self.assertEquals(2, Book.search("Cool Stuff").count())

    def test_print(self):
        book, created = Book.from_dict({"title": "Stuff"})
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        with StringIO() as cout:
            book.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Title                            Stuff                              "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Authors                                                             "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Series                                                              "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Volume                                                              "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Genres                                                              "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Links                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Editions                                                            "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

        book, created = Book.from_dict(
            {
                "title": "Example",
                "authors": [{"name": "Max Mustermann"}],
                "series": {"name": "Secret Files"},
                "volume": 1,
                "genres": [{"name": "Fiction"}],
                "links": [{"url": "https://example.com"}],
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(book.id)

        with StringIO() as cout:
            book.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               2                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Title                            Example                            "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Authors                          1: Max Mustermann                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Series                           1: Secret Files                    "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Volume                           1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Genres                           1: Fiction                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Links                            1: https://example.com             "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Editions                                                            "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n",
                cout.getvalue(),
            )

    def test_save(self):
        book = Book(title="Green Garden")
        book.save()
        self.assertIsNotNone(book.id)
        self.assertEquals("green-garden", book.slug)

        book = Book(title="Old Garden")
        book.save()
        self.assertIsNotNone(book.id)
        self.assertEquals("old-garden", book.slug)


class EditionModelTestCase(TestCase):
    def setUp(self):
        self.book, created = Book.from_dict(
            {
                "title": "Example",
                "authors": [{"name": "Max Mustermann"}],
                "series": {"name": "Secret Files"},
                "volume": 1,
                "genres": [{"name": "Fiction"}],
                "links": [{"url": "https://example.com"}],
            }
        )
        self.assertTrue(created)
        self.assertIsNotNone(self.book.id)

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_from_to_dict(self):
        edition, created = Edition.from_dict({}, self.book)
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)
        self.assertEquals(
            {
                "alternate_title": None,
                "isbn": None,
                "publishing_date": None,
                "cover_image": None,
                "publisher": None,
                "binding": None,
                "languages": None,
                "links": None,
                "persons": None,
                "bibtex": None,
                "files": None,
                "acquisitions": None,
                "reads": None,
            },
            edition.to_dict(),
        )
        self.assertEquals(
            (edition, False), Edition.from_dict(edition.to_dict(), self.book)
        )

        edition, created = Edition.from_dict(
            {
                "alternate_title": "Beispiel",
                "isbn": "9783030637873",
                "publishing_date": "2021-02-01",
                "cover_image": None,
                "publisher": {"name": "Horse"},
                "binding": {"name": "Hardcover"},
                "languages": [{"name": "Englisch"}],
                "links": [{"url": "https://example.com"}],
                "persons": [{"name": "John Do"}],
                "bibtex": None,
                "files": None,
                "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            },
            self.book,
        )
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)
        self.assertEquals(
            {
                "alternate_title": "Beispiel",
                "isbn": "9783030637873",
                "publishing_date": "2021-02-01",
                "cover_image": None,
                "publisher": {"name": "Horse", "links": None},
                "binding": {"name": "Hardcover"},
                "languages": [{"name": "Englisch"}],
                "links": [{"url": "https://example.com"}],
                "persons": [{"name": "John Do", "links": None}],
                "bibtex": None,
                "files": None,
                "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            },
            edition.to_dict(),
        )
        self.assertEquals(
            (edition, False),
            Edition.from_dict(
                {
                    "alternate_title": "Beispiel",
                    "isbn": "9783030637873",
                    "publishing_date": "2021-02-01",
                    "publisher": {"name": "Horse"},
                    "binding": {"name": "Hardcover"},
                    "languages": [{"name": "Englisch"}],
                    "links": [{"url": "https://example.com"}],
                    "persons": [{"name": "John Do"}],
                    "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                    "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
                },
                self.book,
            ),
        )

        with NamedTemporaryFile() as f:
            f.write(b"Lorem ipsum dolorem")

            edition, created = Edition.from_dict(
                {
                    "alternate_title": "Beispiel",
                    "publishing_date": "2021-02-01",
                    "files": [{"path": f.name}],
                },
                self.book,
            )
            self.assertTrue(created)
            self.assertIsNotNone(edition.id)
            self.assertEquals(
                {
                    "alternate_title": "Beispiel",
                    "publishing_date": "2021-02-01",
                    "files": [
                        {
                            "path": str(
                                settings.MEDIA_ROOT
                                / "books"
                                / str(self.book.pk)
                                / str(edition.pk)
                                / os.path.basename(f.name)
                            )
                        }
                    ],
                    "isbn": None,
                    "cover_image": None,
                    "publisher": None,
                    "binding": None,
                    "languages": None,
                    "links": None,
                    "persons": None,
                    "bibtex": None,
                    "acquisitions": None,
                    "reads": None,
                },
                edition.to_dict(),
            )

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_delete(self):
        edition, created = Edition.from_dict(
            {
                "alternate_title": "Beispiel",
                "isbn": "9783030637873",
                "publishing_date": "2021-02-01",
                "publisher": {"name": "Horse"},
                "binding": {"name": "Hardcover"},
                "languages": [{"name": "Englisch"}],
                "links": [{"url": "https://example.com"}],
                "persons": [{"name": "John Do"}],
                "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            },
            self.book,
        )
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)

        with NamedTemporaryFile() as f:
            f.write(b"Lorem ipsum dolorem")
            edition.edit("file", f.name)

        deleted = edition.delete()
        self.assertIsNone(edition.id)
        self.assertEquals(
            (
                8,
                {
                    "bindings.Binding": 1,
                    "books.Edition": 1,
                    "books.Edition_languages": 1,
                    "books.Edition_links": 1,
                    "books.Edition_persons": 1,
                    "files.File": 1,
                    "shelves.Acquisition": 1,
                    "shelves.Read": 1,
                },
            ),
            deleted,
        )

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_edit(self):
        edition, created = Edition.from_dict({}, self.book)
        self.assertTrue(created)

        edition.edit("isbn", "9785423647891")
        self.assertEquals("9785423647891", edition.isbn)

        edition.edit("publishing_date", "2016-06-15")
        self.assertEquals("2016-06-15", edition.publishing_date)

        edition.edit("binding", "Taschenbuch")
        self.assertIsNotNone(edition.binding)
        self.assertIsNotNone(edition.binding.id)
        self.assertEquals("Taschenbuch", edition.binding.name)

        edition.edit("publisher", "Printers")
        self.assertIsNotNone(edition.publisher)
        self.assertIsNotNone(edition.publisher.id)
        self.assertEquals("Printers", edition.publisher.name)

        edition.edit("language", "English")
        self.assertEquals(1, edition.languages.count())
        self.assertEquals("English", edition.languages.first().name)

        edition.edit("language", "Deutsch")
        self.assertEquals(2, edition.languages.count())
        self.assertEquals("Deutsch", edition.languages.first().name)

        edition.edit("language", "English")
        self.assertEquals(1, edition.languages.count())
        self.assertEquals("Deutsch", edition.languages.first().name)

        with NamedTemporaryFile() as f:
            f.write(b"Lorem ipsum dolorem")

            edition.edit("file", f.name)
            self.assertEquals(1, edition.files.count())
        self.assertEquals(
            f"books/{self.book.pk}/{edition.pk}/{os.path.basename(f.name)}",
            edition.files.first().file,
        )

    def test_get(self):
        edition, created = Edition.from_dict(
            {"alternate_title": "Beispiel", "isbn": "9783030637873"}, self.book
        )
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)

        edition2 = Edition.get("Beispiel")
        self.assertIsNotNone(edition)
        self.assertEquals(edition, edition2)

        edition2 = Edition.get("Example")
        self.assertIsNotNone(edition)
        self.assertEquals(edition, edition2)

        edition2 = Edition.get("9783030637873")
        self.assertIsNotNone(edition)
        self.assertEquals(edition, edition2)

        edition2 = Edition.get(str(edition.id))
        self.assertIsNotNone(edition)
        self.assertEquals(edition, edition2)

        edition2 = Edition.get("Secret Files 1")
        self.assertIsNotNone(edition)
        self.assertEquals(edition, edition2)

    def test_search(self):
        edition, created = Edition.from_dict(
            {"alternate_title": "Beispiel", "isbn": "9783030637873"}, self.book
        )
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)

        edition, created = Edition.from_dict(
            {
                "alternate_title": "Eeksempel",
            },
            self.book,
        )
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)

        edition, created = Edition.from_dict(
            {
                "publishing_date": "2021-01-01",
            },
            self.book,
        )
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)

        book, created = Book.from_dict({"title": "Bibliothek"})
        self.assertTrue(created)
        self.assertIsNotNone(self.book.id)

        edition, created = Edition.from_dict(
            {
                "alternate_title": "Beispiel",
            },
            book,
        )
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)

        self.assertEquals(4, Edition.objects.count())
        self.assertEquals(3, Edition.search("", self.book).count())
        self.assertEquals(1, Edition.search("9783030637873").count())

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_print(self):
        edition, created = Edition.from_dict(
            {
                "alternate_title": "Beispiel",
                "isbn": "9783030637873",
                "publishing_date": "2021-02-01",
                "publisher": {"name": "Horse"},
                "binding": {"name": "Hardcover"},
                "languages": [{"name": "Englisch"}],
                "links": [{"url": "https://example.com"}],
                "persons": [{"name": "John Do"}],
                "acquisitions": [{"date": "2021-01-02", "price": 10.0}],
                "reads": [{"started": "2021-01-02", "finished": "2021-01-03"}],
            },
            self.book,
        )
        self.assertTrue(created)
        self.assertIsNotNone(edition.id)

        with NamedTemporaryFile() as f:
            f.write(b"Lorem ipsum dolorem")

            edition.edit("file", f.name)

        self.maxDiff = None
        with StringIO() as cout:
            edition.print(cout)
            self.assertEquals(
                "Field                            Value                              "
                + "                                \n=================================="
                + "==================================================================\n"
                + "Id                               1                                  "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Book                             1: Example - Max Mustermann (Secret"
                + " Files 1)                       \n__________________________________"
                + "__________________________________________________________________\n"
                + "Alternate title                  Beispiel                           "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "ISBN                             9783030637873                      "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Publishing date                  2021-02-01                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Cover                                                               "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Binding                          1: Hardcover                       "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Publisher                        1: Horse                           "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Persons                          2: John Do                         "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Languages                        1: Englisch                        "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Links                            1: https://example.com             "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Files                            1: "
                + f"{os.path.basename(edition.files.first().file.name)}                "
                + "     "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Acquisitions                     1: date=2021-01-02, price=10.00    "
                + "                                \n__________________________________"
                + "__________________________________________________________________\n"
                + "Read                             1: date started=2021-01-02, date fi"
                + "nished=2021-01-03               \n=================================="
                + "==================================================================\n",
                cout.getvalue(),
            )

    @override_settings(MEDIA_ROOT=Path(mkdtemp()))
    def test_save(self):
        edition = Edition(alternate_title="Beispiel")
        edition.book = self.book
        edition.save()
        self.assertIsNotNone(edition.id)

        edition = Edition()
        edition.book = self.book
        edition.publishing_date = datetime.strptime("2021-02-01", "%Y-%m-%d").date()
        edition.save()
        self.assertIsNotNone(edition.id)

        file = File(file=SimpleUploadedFile("test.txt", b"Lorem ipsum dolorem"))
        file.save()
        self.assertIsNotNone(file.id)
        self.assertEquals("files/test.txt", file.file.name)

        edition.files.add(file)
        edition.save()
        self.assertEquals("books/1/2/test.txt", edition.files.first().file.name)
