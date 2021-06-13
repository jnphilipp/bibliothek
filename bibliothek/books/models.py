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
"""Books Django app models."""

import datetime
import hashlib
import os
import shutil
import sys

from bibliothek import stdout
from bibliothek.utils import lookahead
from bindings.models import Binding
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.files import File as DJFile
from django.db import models
from django.db.models import F, Func, Q, Value
from django.db.models.functions import Concat
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from files.models import File
from genres.models import Genre
from languages.models import Language
from links.models import Link
from persons.models import Person
from publishers.models import Publisher
from series.models import Series
from shelves.models import Acquisition, Read
from typing import Dict, Optional, TextIO, Tuple, Type, TypeVar, Union


class Book(models.Model):
    """Book ORM Model."""

    T = TypeVar("T", bound="Book", covariant=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    slug = models.SlugField(max_length=2048, unique=True, verbose_name=_("Slug"))
    title = models.TextField(unique=True, verbose_name=_("Title"))
    authors = models.ManyToManyField(
        Person, blank=True, related_name="books", verbose_name=_("Authors")
    )

    series = models.ForeignKey(
        Series,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="books",
        verbose_name=_("Series"),
    )
    volume = models.FloatField(default=0, blank=True, verbose_name=_("Volume"))

    genres = models.ManyToManyField(
        Genre, blank=True, related_name="books", verbose_name=_("Genres")
    )
    links = models.ManyToManyField(
        Link, blank=True, related_name="books", verbose_name=_("Links")
    )

    @classmethod
    def by_shelf(cls: Type[T], shelf: str) -> models.query.QuerySet[T]:
        """Filter by shelf."""
        assert shelf in ["acquired", "unacquired", "read", "unread"]

        query_set = cls.objects.all()
        if shelf == "acquired":
            query_set = query_set.filter(editions__acquisitions__isnull=False)
        elif shelf == "unacquired":
            query_set = query_set.filter(editions__acquisitions__isnull=True)
        elif shelf == "read":
            query_set = query_set.filter(editions__reads__isnull=False)
        elif shelf == "unread":
            query_set = query_set.filter(editions__reads__isnull=True)
        return query_set.distinct()

    @classmethod
    def from_dict(cls: Type[T], data: Dict) -> Tuple[T, bool]:
        """Create from dict.

        Returns True if was crated, i. e. was not found in the DB.
        """
        defaults: Dict = {}
        if "series" in data and data["series"]:
            defaults["series"] = Series.from_dict(data["series"])[0]
        if "volume" in data and data["volume"]:
            defaults["volume"] = data["volume"]

        book, created = Book.objects.get_or_create(
            title=data["title"], defaults=defaults
        )

        if "authors" in data and data["authors"]:
            for i in data["authors"]:
                book.authors.add(Person.from_dict(i)[0])
        if "genres" in data and data["genres"]:
            for i in data["genres"]:
                book.genres.add(Genre.from_dict(i)[0])
        if "links" in data and data["links"]:
            for i in data["links"]:
                book.links.add(Link.from_dict(i)[0])

        return book, created

    @classmethod
    def get(cls: Type[T], term: str) -> Optional[T]:
        """Search for given term, return single object."""
        query_set = cls.search(term)
        if query_set.count() == 0:
            return None
        elif query_set.count() > 1:
            if term.isdigit():
                query_set = query_set.filter(pk=term)
            else:
                query_set = query_set.filter(title=term)
            if query_set.count() != 1:
                return None
        return query_set[0]

    @classmethod
    def search(cls: Type[T], term: str) -> models.query.QuerySet[T]:
        """Search for given term."""
        persons = Person.objects.filter(
            Q(pk=term if term.isdigit() else None) | Q(name__icontains=term)
        )

        return cls.objects.filter(
            Q(pk=term if term.isdigit() else None)
            | Q(title__icontains=term)
            | Q(authors__in=persons)
            | Q(series__name__icontains=term)
        ).distinct()

    def delete(self: T) -> Tuple[int, Dict[str, int]]:
        """Delete from DB."""

        def append(d: Tuple[int, Dict[str, int]]) -> int:
            for k, v in d[1].items():
                if k in deleted:
                    deleted[k] += v
                else:
                    deleted[k] = v
            return d[0]

        nb_deleted = 0
        deleted: Dict[str, int] = {}
        if self.series and self.series.books.count() == 1:
            nb_deleted += append(self.series.delete())
        for genre in self.genres.all():
            if genre.books.count() == 1:
                nb_deleted += append(genre.delete())
        for link in self.links.all():
            if (
                link.editions.count() == 0
                and link.issues.count() == 0
                and link.publishers.count() == 0
                and link.journals.count() == 0
                and link.books.count() == 1
                and link.magazine_feed.count() == 0
                and link.magazines.count() == 0
                and link.series.count() == 0
                and link.papers.count() == 0
                and link.persons.count() == 0
            ):
                nb_deleted += append(link.delete())
        nb_deleted += append(super(Book, self).delete())
        return nb_deleted, deleted

    def edit(self: T, field: str, value: Union[str, float], *args, **kwargs):
        """Change field by given value."""
        assert field in ["title", "author", "series", "volume", "genre", "link"]

        if field == "title":
            self.title = value
        elif field == "author" and isinstance(value, str):
            author = Person.get_or_create(value)
            if self.authors.filter(pk=author.pk).exists():
                self.authors.remove(author)
            else:
                self.authors.add(author)
        elif field == "series" and isinstance(value, str):
            self.series = Series.get_or_create(value)
        elif field == "volume":
            self.volume = value
        elif field == "genre" and isinstance(value, str):
            genre = Genre.get_or_create(value)
            if self.genres.filter(pk=genre.pk).exists():
                self.genres.remove(genre)
            else:
                self.genres.add(genre)
        elif field == "link" and isinstance(value, str):
            link = Link.get_or_create(value)
            if self.links.filter(pk=link.pk).exists():
                self.links.remove(link)
            else:
                self.links.add(link)
        self.save(*args, **kwargs)

    def print(self: T, file: TextIO = sys.stdout):
        """Print instance info."""
        stdout.write([_("Field"), _("Value")], "=", [0.33], file=file)
        stdout.write([_("Id"), self.pk], positions=[0.33], file=file)
        stdout.write([_("Title"), self.title], positions=[0.33], file=file)

        if self.authors.count() > 0:
            for (i, author), has_next in lookahead(enumerate(self.authors.all())):
                stdout.write(
                    ["" if i else _("Authors"), f"{author.pk}: {author}"],
                    "" if has_next else "_",
                    positions=[0.33],
                    file=file,
                )
        else:
            stdout.write([_("Authors"), ""], positions=[0.33], file=file)

        stdout.write(
            [
                _("Series"),
                f"{self.series.id}: {self.series.name}" if self.series else "",
            ],
            positions=[0.33],
            file=file,
        )
        stdout.write([_("Volume"), self.volume], positions=[0.33], file=file)

        if self.genres.count() > 0:
            for (i, g), has_next in lookahead(enumerate(self.genres.all())):
                stdout.write(
                    ["" if i else _("Genres"), f"{g.id}: {g.name}"],
                    "" if has_next else "_",
                    positions=[0.33],
                    file=file,
                )
        else:
            stdout.write([_("Genres"), ""], positions=[0.33], file=file)

        if self.links.count() > 0:
            for (i, l), has_next in lookahead(enumerate(self.links.all())):
                stdout.write(
                    ["" if i else _("Links"), f"{l.pk}: {l.link}"],
                    "" if has_next else "_",
                    positions=[0.33],
                    file=file,
                )
        else:
            stdout.write([_("Links"), ""], positions=[0.33], file=file)

        if self.editions.count() > 0:
            for (i, edition), has_next in lookahead(enumerate(self.editions.all())):
                s = ""
                if edition.alternate_title:
                    s = f"{edition.alternate_title}, "
                if edition.binding:
                    s += edition.binding.name

                stdout.write(
                    ["" if i else _("Editions"), f"{edition.id}: {s}"],
                    "" if has_next else "_",
                    positions=[0.33],
                    file=file,
                )
        else:
            stdout.write([_("Editions"), ""], positions=[0.33], file=file)

    def save(self, *args, **kwargs):
        """Save in DB."""
        if not self.slug:
            self.slug = slugify(self.title)
        else:
            orig = Book.objects.get(pk=self.id)
            if orig.title != self.title:
                self.slug = slugify(self.title)
        if self.slug is None or self.slug == "":
            self.slug = hashlib.md5(self.title.encode("utf8")).hexdigest()
        super(Book, self).save(*args, **kwargs)

    def to_dict(self: T) -> Dict:
        """Convert to dict."""
        return {
            "title": self.title,
            "authors": [i.to_dict() for i in self.authors.all()]
            if self.authors.count() > 0
            else None,
            "series": self.series.to_dict() if self.series else None,
            "volume": self.volume,
            "genres": [i.to_dict() for i in self.genres.all()]
            if self.genres.count() > 0
            else None,
            "links": [i.to_dict() for i in self.links.all()]
            if self.links.count() > 0
            else None,
        }

    def __str__(self: T) -> str:
        """Name."""
        authors = ", ".join([str(a) for a in self.authors.all()])
        authors = "" if self.authors.count() == 0 else f" - {authors}"
        series = f" ({self.series} {self.volume:g})" if self.series else ""
        return f"{self.title}{authors}{series}"

    class Meta:
        """Meta."""

        ordering = (
            Func(F("series__name"), function="LOWER"),
            "volume",
            Func(F("title"), function="LOWER"),
        )
        verbose_name = _("Book")
        verbose_name_plural = _("Books")


class Edition(models.Model):
    """Book ORM Model."""

    T = TypeVar("T", bound="Edition", covariant=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    alternate_title = models.TextField(
        blank=True, null=True, verbose_name=_("Alternate title")
    )
    book = models.ForeignKey(
        Book, models.CASCADE, related_name="editions", verbose_name=_("Book")
    )
    isbn = models.CharField(
        max_length=13, blank=True, null=True, verbose_name=_("ISBN")
    )
    publishing_date = models.DateField(
        blank=True, null=True, verbose_name=_("Publishing date")
    )
    cover_image = models.ImageField(
        upload_to="files", blank=True, null=True, verbose_name=_("Cover image")
    )
    files = GenericRelation(
        File, related_query_name="editions", verbose_name=_("Files")
    )

    publisher = models.ForeignKey(
        Publisher,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="editions",
        verbose_name=_("Publisher"),
    )
    binding = models.ForeignKey(
        Binding,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="editions",
        verbose_name=_("Binding"),
    )
    languages = models.ManyToManyField(
        Language, blank=True, related_name="editions", verbose_name=_("Languages")
    )
    links = models.ManyToManyField(
        Link, blank=True, related_name="editions", verbose_name=_("Links")
    )
    bibtex = models.TextField(blank=True, null=True, verbose_name=_("BibTex"))
    persons = models.ManyToManyField(
        Person, blank=True, related_name="editions", verbose_name=_("Persons")
    )

    acquisitions = GenericRelation(
        Acquisition,
        related_query_name="editions",
        verbose_name=_("Acquisitions"),
    )
    reads = GenericRelation(
        Read, related_query_name="editions", verbose_name=_("Reads")
    )

    @classmethod
    def by_shelf(
        cls: Type[T], shelf: str, book: Optional[Book] = None
    ) -> models.query.QuerySet[T]:
        """Filter by shelf."""
        assert shelf in ["acquired", "unacquired", "read", "unread"]

        query_set = cls.objects.all()
        if book is not None:
            query_set = query_set.filter(book=book)
        if shelf == "acquired":
            query_set = query_set.filter(acquisitions__isnull=False)
        elif shelf == "unacquired":
            query_set = query_set.filter(acquisitions__isnull=True)
        elif shelf == "read":
            query_set = query_set.filter(reads__isnull=False)
        elif shelf == "unread":
            query_set = query_set.filter(reads__isnull=True)
        return query_set.distinct()

    @classmethod
    def from_dict(cls: Type[T], data: Dict, book: Book) -> Tuple[T, bool]:
        """Create from dict.

        Returns True if was crated, i. e. was not found in the DB.
        """
        defaults: Dict = {}
        if "alternate_title" in data and data["alternate_title"]:
            defaults["alternate_title"] = data["alternate_title"]
        if "isbn" in data and data["isbn"]:
            defaults["isbn"] = data["isbn"]
        if "publishing_date" in data and data["publishing_date"]:
            defaults["publishing_date"] = datetime.datetime.strptime(
                data["publishing_date"], "%Y-%m-%d"
            ).date()
        if "publisher" in data and data["publisher"]:
            defaults["publisher"] = Publisher.from_dict(data["publisher"])[0]
        if "binding" in data and data["binding"]:
            defaults["binding"] = Binding.from_dict(data["binding"])[0]
        if "bibtex" in data and data["bibtex"]:
            defaults["bibtex"] = data["bibtex"]

        edition, created = cls.objects.get_or_create(
            book=book,
            alternate_title=data["alternate_title"]
            if "alternate_title" in data
            else None,
            isbn=data["isbn"] if "isbn" in data else None,
            publishing_date=data["publishing_date"]
            if "publishing_date" in data
            else None,
            defaults=defaults,
        )

        if "cover_image" in data and data["cover_image"]:
            edition.cover_image.save(
                os.path.basename(data["cover_image"]),
                DJFile(open(data["cover_image"], "rb")),
            )
        if "languages" in data and data["languages"]:
            for i in data["languages"]:
                edition.languages.add(Language.from_dict(i)[0])
        if "links" in data and data["links"]:
            for i in data["links"]:
                edition.links.add(Link.from_dict(i)[0])
        if "persons" in data and data["persons"]:
            for i in data["persons"]:
                edition.persons.add(Person.from_dict(i)[0])

        if "acquisitions" in data and data["acquisitions"]:
            for i in data["acquisitions"]:
                Acquisition.from_dict(i, edition)
        if "files" in data and data["files"]:
            for i in data["files"]:
                File.from_dict(i, edition)
        if "reads" in data and data["reads"]:
            for i in data["reads"]:
                Read.from_dict(i, edition)
        edition.save()
        return edition, created

    @classmethod
    def get(cls: Type[T], term: str, book: Optional[Book] = None) -> Optional[T]:
        """Search for given term, return single object."""
        query_set = cls.search(term, book)
        if query_set.count() == 0:
            return None
        elif query_set.count() > 1:
            if term.isdigit():
                query_set = query_set.filter(pk=term)
            else:
                query_set = query_set.filter(
                    Q(alternate_title=term) | Q(isbn=term) | Q(book__title=term)
                )
            if query_set.count() != 1:
                return None
        return query_set[0]

    @classmethod
    def search(
        cls: Type[T],
        term: str,
        book: Optional[Book] = None,
        has_file: Optional[bool] = None,
    ) -> models.query.QuerySet[T]:
        """Search for given term."""
        persons = Person.objects.filter(
            Q(pk=term if term.isdigit() else None) | Q(name__icontains=term)
        )

        query_set = cls.objects.annotate(
            series=Concat(
                "book__series__name",
                Value(" "),
                "book__volume",
                output_field=models.TextField(),
            )
        ).all()
        if book is not None:
            query_set = query_set.filter(book=book)
        if has_file is not None:
            query_set = query_set.filter(files__isnull=not has_file)
        return query_set.filter(
            Q(pk=term if term.isdigit() else None)
            | Q(alternate_title__icontains=term)
            | Q(isbn__icontains=term)
            | Q(persons__in=persons)
            | Q(book__authors__in=persons)
            | Q(series__iregex=term.replace(" ", ".+?"))
            | Q(book__title__icontains=term)
        ).distinct()

    def delete(self: T) -> Tuple[int, Dict[str, int]]:
        """Delete."""

        def append(d: Tuple[int, Dict[str, int]]) -> int:
            for k, v in d[1].items():
                if k in deleted:
                    deleted[k] += v
                else:
                    deleted[k] = v
            return d[0]

        nb_deleted = 0
        deleted: Dict[str, int] = {}
        if self.binding and self.binding.editions.count() == 1:
            nb_deleted += append(self.binding.delete())
        for link in self.links.all():
            if (
                link.editions.count() == 0
                and link.issues.count() == 1
                and link.publishers.count() == 0
                and link.journals.count() == 0
                and link.books.count() == 0
                and link.magazine_feed.count() == 0
                and link.magazines.count() == 0
                and link.series.count() == 0
                and link.papers.count() == 0
                and link.persons.count() == 0
            ):
                nb_deleted += append(link.delete())
        for file in self.files.all():
            if (
                file.editions.count() == 0
                and file.issues.count() == 0
                and file.papers.count() == 1
            ):
                nb_deleted += append(file.delete())
        for acquisition in self.acquisitions.all():
            nb_deleted += append(acquisition.delete())
        for read in self.reads.all():
            nb_deleted += append(read.delete())
        nb_deleted += append(super(Edition, self).delete())
        return nb_deleted, deleted

    def edit(self: T, field: str, value: str, *args, **kwargs):
        """Change field by given value."""
        assert field in [
            "alternate_title",
            "alternate-title",
            "binding",
            "cover",
            "isbn",
            "person",
            "publishing_date",
            "publishing-date",
            "publisher",
            "language",
            "link",
            "file",
        ]

        if field == "alternate_title" or field == "alternate-title":
            self.alternate_title = value
        elif field == "binding":
            self.binding = Binding.get_or_create(value)
        elif field == "cover":
            self.cover_image.save(
                os.path.basename(str(value)), DJFile(open(str(value), "rb"))
            )
        elif field == "isbn":
            self.isbn = value
        elif field == "person":
            person = Person.get_or_create(value)
            if self.persons.filter(pk=person.pk).exists():
                self.persons.remove(person)
            else:
                self.persons.add(person)
        elif field == "publishing_date" or field == "publishing-date":
            self.publishing_date = value
        elif field == "publisher":
            self.publisher = Publisher.get_or_create(value)
        elif field == "language":
            language = Language.get_or_create(value)
            if self.languages.filter(pk=language.pk).exists():
                self.languages.remove(language)
            else:
                self.languages.add(language)
        elif field == "link":
            link = Link.get_or_create(value)
            if self.links.filter(pk=link.pk).exists():
                self.links.remove(link)
            else:
                self.links.add(link)
        elif field == "file":
            file, created = File.from_dict({"path": value})
            if self.files.filter(pk=file.pk).exists():
                self.files.remove(file)
                file.delete()
            else:
                self.files.add(file)
        self.save(*args, **kwargs)

    def get_title(self):
        """Get title."""
        if self.alternate_title:
            return self.alternate_title
        else:
            return self.book.title

    def print(self: T, file: TextIO = sys.stdout):
        """Print instance info."""
        stdout.write([_("Field"), _("Value")], "=", [0.33], file=file)
        stdout.write([_("Id"), self.pk], positions=[0.33], file=file)
        stdout.write(
            [_("Book"), f"{self.book.pk}: {self.book}"], positions=[0.33], file=file
        )
        stdout.write(
            [_("Alternate title"), self.alternate_title], positions=[0.33], file=file
        )
        stdout.write([_("ISBN"), self.isbn], positions=[0.33], file=file)
        stdout.write(
            [_("Publishing date"), self.publishing_date], positions=[0.33], file=file
        )
        stdout.write([_("Cover"), self.cover_image], positions=[0.33], file=file)
        stdout.write(
            [
                _("Binding"),
                f"{self.binding.pk}: {self.binding.name}" if self.binding else "",
            ],
            positions=[0.33],
            file=file,
        )
        stdout.write(
            [
                _("Publisher"),
                f"{self.publisher.pk}: {self.publisher.name}" if self.publisher else "",
            ],
            positions=[0.33],
            file=file,
        )

        if self.persons.count() > 0:
            for (i, p), has_next in lookahead(enumerate(self.persons.all())):
                stdout.write(
                    ["" if i else _("Persons"), f"{p.pk}: {p.name}"],
                    "" if has_next else "_",
                    positions=[0.33],
                    file=file,
                )
        else:
            stdout.write([_("Persons"), ""], positions=[0.33], file=file)

        if self.languages.count() > 0:
            for (i, l), has_next in lookahead(enumerate(self.languages.all())):
                stdout.write(
                    ["" if i else _("Languages"), f"{l.pk}: {l.name}"],
                    "" if has_next else "_",
                    positions=[0.33],
                    file=file,
                )
        else:
            stdout.write([_("Languages"), ""], positions=[0.33], file=file)

        if self.links.count() > 0:
            for (i, l), has_next in lookahead(enumerate(self.links.all())):
                stdout.write(
                    ["" if i else _("Links"), f"{l.pk}: {l.link}"],
                    "" if has_next else "_",
                    positions=[0.33],
                    file=file,
                )
        else:
            stdout.write([_("Links"), ""], positions=[0.33], file=file)

        if self.files.count() > 0:
            for (i, f), has_next in lookahead(enumerate(self.files.all())):
                stdout.write(
                    ["" if i else _("Files"), f"{f.pk}: {f}"],
                    "" if has_next else "_",
                    positions=[0.33],
                    file=file,
                )
        else:
            stdout.write([_("Files"), ""], positions=[0.33], file=file)

        if self.acquisitions.count() > 0:
            for (i, a), has_next in lookahead(enumerate(self.acquisitions.all())):
                stdout.write(
                    [
                        "" if i else _("Acquisitions"),
                        f"{a.pk}: {_('date')}={a.date}, {_('price')}={a.price:0.2f}",
                    ],
                    "" if has_next else "_",
                    positions=[0.33],
                    file=file,
                )
        else:
            stdout.write([_("Acquisitions"), ""], positions=[0.33], file=file)

        if self.reads.count() > 0:
            for (i, r), has_next in lookahead(enumerate(self.reads.all())):
                stdout.write(
                    [
                        "" if i else _("Read"),
                        f"{r.pk}: {_('date started')}={r.started}, "
                        + f"{_('date finished')}={r.finished}",
                    ],
                    "" if has_next else "=",
                    positions=[0.33],
                    file=file,
                )
        else:
            stdout.write([_("Read"), ""], positions=[0.33], file=file)

    def save(self, *args, **kwargs):
        """Save."""
        path = os.path.join("books", str(self.book.id), str(self.id))
        if self.cover_image and not self.cover_image.name.startswith(path):
            self._move_cover_image()
        super(Edition, self).save(*args, **kwargs)
        for file in self.files.all():
            if not file.file.name.startswith(path):
                self._move_file(file)

    def to_dict(self: T) -> Dict:
        """Convert to dict."""
        return {
            "alternate_title": self.alternate_title,
            "isbn": self.isbn,
            "publishing_date": self.publishing_date.strftime("%Y-%m-%d")
            if self.publishing_date
            else None,
            "cover_image": self.cover_image.path if self.cover_image else None,
            "publisher": self.publisher.to_dict() if self.publisher else None,
            "binding": self.binding.to_dict() if self.binding else None,
            "languages": [i.to_dict() for i in self.languages.all()]
            if self.languages.count() > 0
            else None,
            "links": [i.to_dict() for i in self.links.all()]
            if self.links.count() > 0
            else None,
            "persons": [i.to_dict() for i in self.persons.all()]
            if self.persons.count() > 0
            else None,
            "bibtex": self.bibtex,
            "files": [i.to_dict() for i in self.files.all()]
            if self.files.count() > 0
            else None,
            "acquisitions": [i.to_dict() for i in self.acquisitions.all()]
            if self.acquisitions.count() > 0
            else None,
            "reads": [i.to_dict() for i in self.reads.all()]
            if self.reads.count() > 0
            else None,
        }

    def _move_cover_image(self):
        ending = os.path.splitext(self.cover_image.name)[1]
        save_name = os.path.join(
            "books", str(self.book.id), str(self.id), f"cover{ending}"
        )

        current_path = os.path.join(settings.MEDIA_ROOT, self.cover_image.name)
        new_path = os.path.join(settings.MEDIA_ROOT, save_name)

        if os.path.exists(current_path) and current_path != new_path:
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            shutil.move(current_path, new_path)
            self.cover_image.name = save_name

    def _move_file(self: T, file: File):
        save_name = os.path.join(
            "books", str(self.book.id), str(self.id), os.path.basename(file.file.name)
        )

        new_path = settings.MEDIA_ROOT / save_name
        if os.path.exists(file.file.path) and file.file.path != new_path:
            if not new_path.parent.exists():
                new_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(file.file.path, new_path)
            file.file.name = save_name
            file.save()

    def __str__(self):
        """Name."""
        authors = ", ".join([f"{a}" for a in self.book.authors.all()])
        authors = "" if self.book.authors.count() == 0 else f" - {authors}"
        series = ""
        if self.book.series:
            series = f" ({self.book.series} {self.book.volume:g})"
        return f"{self.get_title()}{authors}{series} #{self.id}"

    class Meta:
        """Meta."""

        ordering = (
            Func(F("book__series__name"), function="LOWER"),
            "book__volume",
            Func(F("book__title"), function="LOWER"),
            "publishing_date",
        )
        verbose_name = _("Edition")
        verbose_name_plural = _("Editions")
