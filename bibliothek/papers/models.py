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
"""Papers Django app models."""

import datetime
import os
import re
import shutil
import sys

from bibliothek import stdout
from bibliothek.utils import lookahead
from bibtexparser.bparser import BibTexParser
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import F, Func, Q, Value
from django.db.models.functions import Concat
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from files.models import File
from journals.models import Journal
from languages.models import Language
from links.models import Link
from persons.models import Person
from publishers.models import Publisher
from series.models import Series
from shelves.models import Acquisition, Read
from typing import Dict, List, Optional, TextIO, Tuple, Type, TypeVar, Union


class Paper(models.Model):
    """Paper Model."""

    T = TypeVar("T", bound="Paper", covariant=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    slug = models.SlugField(max_length=2048, unique=True, verbose_name=_("Slug"))
    title = models.TextField(unique=True, verbose_name=_("Title"))
    authors = models.ManyToManyField(
        Person, blank=True, related_name="papers", verbose_name=_("Authors")
    )
    publishing_date = models.DateField(
        blank=True, null=True, verbose_name=_("Publishing date")
    )
    doi = models.TextField(blank=True, null=True, unique=True, verbose_name=_("DOI"))

    journal = models.ForeignKey(
        Journal,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="papers",
        verbose_name=_("Journal"),
    )
    volume = models.TextField(blank=True, null=True, verbose_name=_("Volume"))
    publisher = models.ForeignKey(
        Publisher,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="papers",
        verbose_name=_("Publisher"),
    )
    series = models.ForeignKey(
        Series,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="papers",
        verbose_name=_("Series"),
    )
    languages = models.ManyToManyField(
        Language, blank=True, related_name="papers", verbose_name=_("Languages")
    )

    files = GenericRelation(File, related_query_name="papers", verbose_name=_("Files"))
    bibtex = models.TextField(blank=True, null=True, verbose_name=_("BibTex"))

    links = models.ManyToManyField(
        Link, blank=True, related_name="papers", verbose_name=_("Links")
    )

    acquisitions = GenericRelation(
        Acquisition, related_query_name="papers", verbose_name=_("Acquisitions")
    )
    reads = GenericRelation(Read, related_query_name="papers", verbose_name=_("Reads"))

    @classmethod
    def by_shelf(cls: Type[T], shelf: str) -> models.query.QuerySet[T]:
        """Filter by shelf."""
        assert shelf in ["acquired", "unacquired", "read", "unread"]

        query_set = cls.objects.all()
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
    def from_bibfile(
        cls: Type[T], path: str, files: List[str] = []
    ) -> List[Tuple[T, bool]]:
        """Create from bibfile."""
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_bibtex(f.read(), files, path)

    @classmethod
    def from_bibtex(
        cls: Type[T], bibtex: str, files: List[str] = [], bibfile: Optional[str] = None
    ) -> List[Tuple[T, bool]]:
        """Create from bibtext."""
        bib_database = BibTexParser(common_strings=True, homogenize_fields=True).parse(
            bibtex
        )

        if len(files) < len(bib_database.entries):
            for i in range(len(files), len(bib_database.entries)):
                files.append("")

        papers = []
        for entry, file in zip(bib_database.entries, files):
            if entry["ENTRYTYPE"] not in [
                "article",
                "inproceedings",
                "phdthesis",
                "inbook",
                "incollection",
                "conference",
            ]:
                continue

            title = entry["title"].strip() if "title" in entry else ""

            authors = []
            entry["author"] = re.sub(r"\s*\n\s*", " ", entry["author"], flags=re.S)
            for author in re.compile(r"\s+and\s+").split(entry["author"]):
                if "," in author:
                    s = author.split(",")
                    authors.append({"name": f"{s[1].strip()} {s[0].strip()}"})
                else:
                    authors.append({"name": author.strip()})

            journal = {"name": entry["journal"].strip()} if "journal" in entry else None

            volume = entry["volume"].strip() if "volume" in entry else None
            if "number" in entry:
                volume = f"{volume}.{entry['number']}" if volume else entry["number"]
            if "eprint" in entry and not volume:
                volume = entry["eprint"].strip()

            publisher = (
                {"name": entry["publisher"].strip()} if "publisher" in entry else None
            )
            series = {"name": entry["series"].strip()} if "series" in entry else None

            year = int(entry["year"].strip()) if "year" in entry else None
            month = entry["month"].strip() if "month" in entry else None
            day = entry["day"].strip() if "day" in entry else None
            if year and month and day:
                try:
                    date = datetime.datetime.strptime(
                        f"{day} {month} {year}", "%d %B %Y"
                    )
                except ValueError:
                    date = datetime.datetime.strptime(
                        f"{day} {month} {year}", "%d %b %Y"
                    )
            elif year and month:
                try:
                    date = datetime.datetime.strptime(f"{month} {year}", "%B %Y")
                except ValueError:
                    date = datetime.datetime.strptime(f"{month} {year}", "%b %Y")
            elif year:
                date = datetime.datetime(year, 1, 1)

            pub_date = None
            if "timestamp" in entry:
                pub_date = (
                    datetime.datetime.strptime(
                        entry["timestamp"].strip(), "%a, %d %b %Y %H:%M:%S %z"
                    )
                    .date()
                    .strftime("%Y-%m-%d")
                )
            elif date:
                pub_date = date.date().strftime("%Y-%m-%d")

            if "link" in entry:
                url: Optional[Dict] = {"url": entry["link"].strip()}
            elif "url" in entry:
                url = {"url": entry["url"].strip()}
            else:
                url = None

            doi = None
            if "doi" in entry:
                if entry["doi"].startswith("doi:"):
                    doi = entry["doi"][4:]
                elif entry["doi"].startswith("http"):
                    doi = re.sub(r"https?://[^/]+/", "", entry["doi"])
                else:
                    doi = entry["doi"]

            papers.append(
                cls.from_dict(
                    {
                        "title": title,
                        "authors": authors,
                        "journal": journal,
                        "volume": volume,
                        "publisher": publisher,
                        "series": series,
                        "publishing_date": pub_date,
                        "links": [url] if url else None,
                        "bibtex": bibtex,
                        "doi": doi,
                    }
                )
            )

            if file:
                papers[-1][0].files.add(File.from_dict({"path": file})[0])
                papers[-1][0].save()
            if bibfile:
                papers[-1][0].files.add(File.from_dict({"path": bibfile})[0])
                papers[-1][0].save()
        return papers

    @classmethod
    def from_dict(cls: Type[T], data: Dict) -> Tuple[T, bool]:
        """Create from dict.

        Returns True if was crated, i. e. was not found in the DB.
        """
        defaults: Dict = {}
        if "journal" in data and data["journal"]:
            defaults["journal"] = Journal.from_dict(data["journal"])[0]
        if "volume" in data and data["volume"]:
            defaults["volume"] = data["volume"]
        if "doi" in data and data["doi"]:
            defaults["doi"] = data["doi"]
        if "publisher" in data and data["publisher"]:
            defaults["publisher"] = Publisher.from_dict(data["publisher"])[0]
        if "series" in data and data["series"]:
            defaults["series"] = Series.from_dict(data["series"])[0]
        if "publishing_date" in data and data["publishing_date"]:
            defaults["publishing_date"] = (
                data["publishing_date"]
                if isinstance(data["publishing_date"], datetime.date)
                else datetime.datetime.strptime(
                    data["publishing_date"], "%Y-%m-%d"
                ).date()
            )
        if "bibtex" in data and data["bibtex"]:
            defaults["bibtex"] = data["bibtex"]

        paper, created = cls.objects.get_or_create(
            title=data["title"], defaults=defaults
        )

        if "authors" in data and data["authors"]:
            for i in data["authors"]:
                paper.authors.add(Person.from_dict(i)[0])
        if "languages" in data and data["languages"]:
            for i in data["languages"]:
                paper.languages.add(Language.from_dict(i)[0])
        if "links" in data and data["links"]:
            for i in data["links"]:
                paper.links.add(Link.from_dict(i)[0])

        if "acquisitions" in data and data["acquisitions"]:
            for i in data["acquisitions"]:
                Acquisition.from_dict(i, paper)
        if "files" in data and data["files"]:
            for i in data["files"]:
                File.from_dict(i, paper)
        if "reads" in data and data["reads"]:
            for i in data["reads"]:
                Read.from_dict(i, paper)
        paper.save()
        return paper, created

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
                query_set = query_set.filter(Q(title=term) | Q(jv=term))
            if query_set.count() != 1:
                return None
        return query_set[0]

    @classmethod
    def search(
        cls: Type[T], term: str, has_file: Optional[bool] = None
    ) -> models.query.QuerySet[T]:
        """Search for given term."""
        persons = Person.objects.filter(
            Q(pk=term if term.isdigit() else None) | Q(name__icontains=term)
        )

        query_set = cls.objects.annotate(
            jv=Concat(
                "journal__name", Value(" "), "volume", output_field=models.TextField()
            )
        ).all()
        if has_file is not None:
            query_set = query_set.filter(files__isnull=not has_file)
        return query_set.filter(
            Q(pk=term if term.isdigit() else None)
            | Q(title__icontains=term)
            | Q(authors__in=persons)
            | Q(jv__icontains=term)
            | Q(doi__icontains=term)
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
        for link in self.links.all():
            if link.num_related("papers") == 0:
                nb_deleted += append(link.delete())
        for file in self.files.all():
            if file.num_related("papers") == 0:
                nb_deleted += append(file.delete())
        for acquisition in self.acquisitions.all():
            nb_deleted += append(acquisition.delete())
        for read in self.reads.all():
            nb_deleted += append(read.delete())
        nb_deleted += append(super(Paper, self).delete())
        return nb_deleted, deleted

    def edit(
        self: T, field: str, value: Optional[Union[str, datetime.date]], *args, **kwargs
    ):
        """Change field by given value."""
        assert field in [
            "title",
            "author",
            "publishing_date",
            "publishing-date",
            "journal",
            "volume",
            "doi",
            "publisher",
            "series",
            "language",
            "file",
            "link",
            "bibtex",
        ]
        if isinstance(value, str) and (
            value.lower() == "none" or value.lower() == "null"
        ):
            value = None
        elif isinstance(value, datetime.date) and field not in [
            "publishing_date",
            "publishing-date",
        ]:
            raise RuntimeError("Date type only allowed with publishing_date field.")

        if field == "title" and not value:
            self.title = value
        elif field == "author" and isinstance(value, str):
            author = Person.get_or_create(value)
            if self.authors.filter(pk=author.pk).exists():
                self.authors.remove(author)
            else:
                self.authors.add(author)
        elif field == "publishing_date" or field == "publishing-date":
            self.publishing_date = (
                value
                if isinstance(value, datetime.date) or value is None
                else datetime.datetime.strptime(value, "%Y-%m-%d").date()
            )
        elif field == "journal" and isinstance(value, str):
            self.journal = Journal.get_or_create(value)
        elif field == "volume":
            self.volume = value
        elif field == "doi":
            self.doi = value
        elif field == "publisher" and isinstance(value, str):
            self.publisher = Publisher.get_or_create(value)
        elif field == "series" and isinstance(value, str):
            self.series = Series.get_or_create(value)
        elif field == "bibtex":
            self.bibtex = value
        elif field == "language" and isinstance(value, str):
            language = Language.get_or_create(value)
            if self.languages.filter(pk=language.pk).exists():
                self.languages.remove(language)
            else:
                self.languages.add(language)
        elif field == "link" and isinstance(value, str):
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
        else:
            raise ValueError("Combination of field and value not allowed.")
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
                _("Journal"),
                f"{self.journal.pk}: {self.journal.name}" if self.journal else "",
            ],
            positions=[0.33],
            file=file,
        )
        stdout.write(
            [_("Volume"), self.volume if self.volume else ""],
            positions=[0.33],
            file=file,
        )
        stdout.write(
            [_("DOI"), self.doi if self.doi else ""],
            positions=[0.33],
            file=file,
        )
        stdout.write(
            [_("Publishing date"), self.publishing_date], positions=[0.33], file=file
        )
        stdout.write(
            [
                _("Publisher"),
                f"{self.publisher.pk}: {self.publisher.name}" if self.publisher else "",
            ],
            positions=[0.33],
            file=file,
        )
        stdout.write(
            [
                _("Series"),
                f"{self.series.pk}: {self.series.name}" if self.series else "",
            ],
            positions=[0.33],
            file=file,
        )

        if self.languages.count() > 0:
            for (i, l), has_next in lookahead(enumerate(self.languages.all())):
                stdout.write(
                    ["" if i else _("Languages"), f"{l.pk}: {l}"],
                    "" if has_next else "_",
                    positions=[0.33],
                    file=file,
                )
        else:
            stdout.write([_("Languages"), ""], positions=[0.33], file=file)

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

        if self.acquisitions.count() > 0:
            date_trans = _("date")
            price_trans = _("price")
            for (i, a), has_next in lookahead(enumerate(self.acquisitions.all())):
                s = f"{a.pk}: {date_trans}={a.date}, {price_trans}={a.price:0.2f}"
                stdout.write(
                    ["" if i else _("Acquisitions"), s],
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
                        "" if i else _("Reads"),
                        f"{r.pk}: {_('date started')}={r.started}, "
                        + f"{_('date finished')}={r.finished}",
                    ],
                    "" if has_next else "_",
                    positions=[0.33],
                    file=file,
                )
        else:
            stdout.write([_("Reads"), ""], positions=[0.33], file=file)

    def save(self: T, *args, **kwargs):
        """Save in DB."""
        if not self.slug:
            self.slug = slugify(self.title)
        else:
            orig = Paper.objects.get(pk=self.pk)
            if orig.title != self.title:
                self.slug = slugify(self.title)
        super(Paper, self).save(*args, **kwargs)
        for file in self.files.all():
            path = os.path.join("papers", str(self.pk))
            if not file.file.name.startswith(path):
                self._move_file(file)

    def to_dict(self: T) -> Dict:
        """Convert to dict."""
        return {
            "title": self.title,
            "authors": [i.to_dict() for i in self.authors.all()]
            if self.authors.count() > 0
            else None,
            "journal": self.journal.to_dict() if self.journal else None,
            "volume": self.volume,
            "doi": self.doi,
            "publisher": self.publisher.to_dict() if self.publisher else None,
            "series": self.series.to_dict() if self.series else None,
            "publishing_date": self.publishing_date.strftime("%Y-%m-%d")
            if self.publishing_date
            else None,
            "languages": [i.to_dict() for i in self.languages.all()]
            if self.languages.count() > 0
            else None,
            "files": [i.to_dict() for i in self.files.all()]
            if self.files.count() > 0
            else None,
            "bibtex": self.bibtex,
            "links": [i.to_dict() for i in self.links.all()]
            if self.links.count() > 0
            else None,
            "acquisitions": [i.to_dict() for i in self.acquisitions.all()]
            if self.acquisitions.count() > 0
            else None,
            "reads": [i.to_dict() for i in self.reads.all()]
            if self.reads.count() > 0
            else None,
        }

    def _move_file(self: T, file: File):
        save_name = os.path.join(
            "papers", str(self.pk), os.path.basename(file.file.name)
        )

        new_path = settings.MEDIA_ROOT / save_name
        if os.path.exists(file.file.path) and file.file.path != new_path:
            if not new_path.parent.exists():
                new_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(file.file.path, new_path)
            file.file.name = save_name
            file.save()

    def __str__(self: T) -> str:
        """Name."""
        if self.authors.count() == 0:
            return self.title
        else:
            return f"{self.title} - {', '.join([str(a) for a in self.authors.all()])}"

    class Meta:
        """Meta."""

        ordering = (
            Func(F("journal__name"), function="LOWER"),
            Func(F("volume"), function="LOWER"),
            Func(F("series__name"), function="LOWER"),
            Func(F("title"), function="LOWER"),
        )
        unique_together = ("journal", "volume", "title")
        verbose_name = _("Paper")
        verbose_name_plural = _("Papers")
