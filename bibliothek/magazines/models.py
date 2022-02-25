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
"""Magazines Django app models."""

import datetime
import os
import shutil
import sys

from bibliothek import stdout
from bibliothek.utils import concat, lookahead
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.files import File as DJFile
from django.db import models
from django.db.models import F, Func, Q, Value
from django.db.models.functions import Concat
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from files.models import File
from languages.models import Language
from links.models import Link
from shelves.models import Acquisition, Read
from typing import Dict, Optional, TextIO, Tuple, Type, TypeVar, Union


class Magazine(models.Model):
    """Magazine Model."""

    T = TypeVar("T", bound="Magazine", covariant=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    slug = models.SlugField(max_length=2048, unique=True, verbose_name=_("Slug"))
    name = models.TextField(unique=True, verbose_name=_("Name"))

    feed = models.ForeignKey(
        Link,
        models.SET_NULL,
        related_name="magazine_feed",
        blank=True,
        null=True,
        verbose_name=_("Feed"),
    )
    links = models.ManyToManyField(
        Link, blank=True, related_name="magazines", verbose_name=_("Links")
    )

    @classmethod
    def from_dict(cls: Type[T], data: Dict) -> Tuple[T, bool]:
        """Create from dict.

        Returns True if was crated, i. e. was not found in the DB.
        """
        defaults: Dict = {}
        if "feed" in data and data["feed"]:
            defaults["feed"] = Link.from_dict(data["feed"])[0]

        magazine, created = cls.objects.get_or_create(
            name=data["name"], defaults=defaults
        )

        if "links" in data and data["links"]:
            for i in data["links"]:
                magazine.links.add(Link.from_dict(i)[0])
        return magazine, created

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
    def search(cls: Type[T], term: str) -> models.query.QuerySet[T]:
        """Search for given term."""
        return cls.objects.filter(
            Q(pk=term if term.isdigit() else None) | Q(name__icontains=term)
        )

    def delete(self: T) -> Tuple[int, Dict[str, int]]:
        """Delete."""
        deleted: Tuple[int, Dict[str, int]] = (0, dict())
        if self.feed and self.feed.num_related("magazine_feed") == 0:
            deleted = concat(deleted, self.feed.delete())
        for link in self.links.all():
            if link.num_related("magazines") == 0:
                deleted = concat(deleted, link.delete())
        return concat(deleted, super(Magazine, self).delete())

    def edit(self: T, field: str, value: str, *args, **kwargs):
        """Change field by given value."""
        assert field in ["name", "feed", "link"]

        if field == "name":
            self.name = value
        elif field == "feed":
            self.feed = Link.get_or_create(value)
        elif field == "link":
            link = Link.get_or_create(value)
            if self.links.filter(pk=link.pk).exists():
                self.links.remove(link)
            else:
                self.links.add(link)
        self.save()

    def print(self: T, file: TextIO = sys.stdout):
        """Print instance info."""
        stdout.write([_("Field"), _("Value")], "=", [0.33], file=file)
        stdout.write([_("Id"), self.pk], positions=[0.33], file=file)
        stdout.write([_("Name"), self.name], positions=[0.33], file=file)
        stdout.write(
            [_("Feed"), f"{self.feed.id}: {self.feed.link}" if self.feed else ""],
            positions=[0.33],
            file=file,
        )

        if self.links.count() > 0:
            for (i, link), has_next in lookahead(enumerate(self.links.all())):
                stdout.write(
                    ["" if i else _("Links"), f"{link.id}: {link.link}"],
                    "" if has_next else "_",
                    positions=[0.33],
                    file=file,
                )
        else:
            stdout.write([_("Links"), ""], positions=[0.33], file=file)

        if self.issues.count() > 0:
            issues = self.issues.all().order_by("publishing_date")
            for (i, issue), has_next in lookahead(enumerate(issues)):
                stdout.write(
                    ["" if i else _("Issue"), f"{issue.id}: {issue.issue}"],
                    "" if has_next else "_",
                    positions=[0.33],
                    file=file,
                )
        else:
            stdout.write([_("Issue"), ""], positions=[0.33], file=file)

    def save(self: T, *args, **kwargs):
        """Save."""
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            orig = Magazine.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(self.name)
        super(Magazine, self).save(*args, **kwargs)

    def to_dict(self: T) -> Dict:
        """Convert to dict."""
        return {
            "name": self.name,
            "feed": self.feed.to_dict() if self.feed else None,
            "links": [i.to_dict() for i in self.links.all()]
            if self.links.count() > 0
            else None,
        }

    def __str__(self) -> str:
        """Name."""
        return self.name

    class Meta:
        """Meta."""

        ordering = (Func(F("name"), function="LOWER"),)
        verbose_name = _("Magazine")
        verbose_name_plural = _("Magazines")


class Issue(models.Model):
    """Issue Model."""

    T = TypeVar("T", bound="Issue", covariant=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    issue = models.TextField(verbose_name=_("Issue"))
    magazine = models.ForeignKey(
        Magazine, models.CASCADE, related_name="issues", verbose_name=_("Magazine")
    )
    publishing_date = models.DateField(
        blank=True, null=True, verbose_name=_("Publishing date")
    )
    languages = models.ManyToManyField(
        Language, blank=True, related_name="issues", verbose_name=_("Languages")
    )

    files = GenericRelation(File, related_query_name="issues", verbose_name=_("Files"))
    cover_image = models.ImageField(
        upload_to="files", blank=True, null=True, verbose_name=_("Cover image")
    )
    links = models.ManyToManyField(
        Link, blank=True, related_name="issues", verbose_name=_("Links")
    )

    acquisitions = GenericRelation(
        Acquisition, related_query_name="issues", verbose_name=_("Acquisitions")
    )
    reads = GenericRelation(Read, related_query_name="issues", verbose_name=_("Reads"))

    @classmethod
    def by_shelf(
        cls: Type[T], shelf: str, magazine: Optional[Magazine] = None
    ) -> models.query.QuerySet[T]:
        """Filter by shelf."""
        assert shelf in ["acquired", "unacquired", "read", "unread"]

        query_set = cls.objects.all()
        if magazine is not None:
            query_set = query_set.filter(magazine=magazine)
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
    def from_dict(cls: Type[T], data: Dict, magazine: Magazine) -> Tuple[T, bool]:
        """Create from dict.

        Returns True if was crated, i. e. was not found in the DB.
        """
        defaults: Dict = {}
        if "publishing_date" in data and data["publishing_date"]:
            defaults["publishing_date"] = (
                data["publishing_date"]
                if isinstance(data["publishing_date"], datetime.date)
                else datetime.datetime.strptime(
                    data["publishing_date"], "%Y-%m-%d"
                ).date()
            )

        issue, created = cls.objects.get_or_create(
            issue=data["issue"], magazine=magazine, defaults=defaults
        )

        if "cover" in data and data["cover"]:
            issue.cover_image.save(
                os.path.basename(data["cover"]),
                DJFile(open(data["cover"], "rb")),
            )
        if "languages" in data and data["languages"]:
            for i in data["languages"]:
                if type(i) == dict:
                    issue.languages.add(Language.from_dict(i)[0])
                else:
                    issue.languages.add(Language.get_or_create(i))
        if "links" in data and data["links"]:
            for i in data["links"]:
                issue.links.add(Link.from_dict(i)[0])

        if "acquisitions" in data and data["acquisitions"]:
            for i in data["acquisitions"]:
                Acquisition.from_dict(i, issue)
        if "files" in data and data["files"]:
            for i in data["files"]:
                File.from_dict(i, issue)
        if "reads" in data and data["reads"]:
            for i in data["reads"]:
                Read.from_dict(i, issue)
        issue.save()
        return issue, created

    @classmethod
    def get(
        cls: Type[T], term: str, magazine: Optional[Magazine] = None
    ) -> Optional[T]:
        """Search for given term, return single object."""
        query_set = cls.search(term, magazine)
        if query_set.count() == 0:
            return None
        elif query_set.count() > 1:
            if term.isdigit():
                query_set = query_set.filter(pk=term)
            else:
                query_set = query_set.filter(Q(issue=term) | Q(name=term))
            if query_set.count() != 1:
                return None
        return query_set[0]

    @classmethod
    def search(
        cls: Type[T],
        term: str,
        magazine: Optional[Magazine] = None,
        has_file: Optional[bool] = None,
    ) -> models.query.QuerySet[T]:
        """Search for given term."""
        query_set = cls.objects.annotate(
            name=Concat(
                "magazine__name", Value(" "), "issue", output_field=models.TextField()
            )
        ).all()
        if magazine is not None:
            query_set = query_set.filter(magazine=magazine)
        if has_file is not None:
            query_set = query_set.filter(files__isnull=not has_file)
        return query_set.filter(
            Q(pk=term if term.isdigit() else None)
            | Q(name__iregex=term.replace(" ", ".+?"))
        )

    def delete(self: T) -> Tuple[int, Dict[str, int]]:
        """Delete."""
        deleted: Tuple[int, Dict[str, int]] = (0, dict())
        for link in self.links.all():
            if link.num_related("issues") == 0:
                deleted = concat(deleted, link.delete())
        for file in self.files.all():
            if file.num_related("issues") == 0:
                deleted = concat(deleted, file.delete())
        for acquisition in self.acquisitions.all():
            deleted = concat(deleted, acquisition.delete())
        for read in self.reads.all():
            deleted = concat(deleted, read.delete())
        return concat(deleted, super(Issue, self).delete())

    def edit(self: T, field: str, value: Union[str, datetime.date], *args, **kwargs):
        """Change field by given value."""
        fields = [
            "issue",
            "publishing_date",
            "publishing-date",
            "cover",
            "language",
            "file",
            "link",
        ]
        assert field in fields

        if field == "issue":
            self.issue = value
        elif field == "publishing_date" or field == "publishing-date":
            self.publishing_date = value
        elif field == "cover":
            self.cover_image.save(
                os.path.basename(str(value)), DJFile(open(str(value), "rb"))
            )
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
        elif field == "file" and isinstance(value, str):
            file, created = File.from_dict({"path": value})
            if self.files.filter(pk=file.pk).exists():
                self.files.remove(file)
                file.delete()
            else:
                self.files.add(file)
        self.save(*args, **kwargs)

    def print(self: T, file: TextIO = sys.stdout):
        """Print instance info."""
        stdout.write([_("Field"), _("Value")], "=", [0.33], file=file)
        stdout.write([_("Id"), self.pk], positions=[0.33], file=file)
        stdout.write(
            [_("Magazine"), f"{self.magazine.pk}: {self.magazine.name}"],
            positions=[0.33],
            file=file,
        )
        stdout.write([_("Issue"), self.issue], positions=[0.33], file=file)
        stdout.write(
            [_("Publishing date"), self.publishing_date], positions=[0.33], file=file
        )
        stdout.write([_("Cover"), self.cover_image], positions=[0.33], file=file)

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
        if self.cover_image and not self.cover_image.name.startswith("magazines"):
            self._move_cover_image()
        super(Issue, self).save(*args, **kwargs)
        for file in self.files.all():
            path = os.path.join("magazines", str(self.id))
            if not file.file.name.startswith(path):
                self._move_file(file)

    def to_dict(self: T) -> Dict:
        """Convert to dict."""
        return {
            "issue": self.issue,
            "publishing_date": self.publishing_date.strftime("%Y-%m-%d")
            if self.publishing_date
            else None,
            "cover": self.cover_image.path if self.cover_image else None,
            "languages": [i.to_dict() for i in self.languages.all()]
            if self.languages.count() > 0
            else None,
            "links": [i.to_dict() for i in self.links.all()]
            if self.links.count() > 0
            else None,
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
        save_name = os.path.join(
            "magazines",
            str(self.magazine.id),
            str(self.id),
            f"cover{os.path.splitext(self.cover_image.name)[1]}",
        )

        new_path = settings.MEDIA_ROOT / save_name
        if os.path.exists(self.cover_image.path) and self.cover_image.path != new_path:
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            shutil.move(self.cover_image.path, new_path)
            self.cover_image.name = save_name

    def _move_file(self: T, file: File):
        save_name = os.path.join(
            "magazines",
            str(self.magazine.id),
            str(self.id),
            os.path.basename(file.file.name),
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
        return f"{self.magazine.name} {self.issue}"

    class Meta:
        """Meta."""

        ordering = (
            Func(F("magazine__name"), function="LOWER"),
            Func(F("issue"), function="LOWER"),
        )
        unique_together = ("magazine", "issue")
        verbose_name = _("Issue")
        verbose_name_plural = _("Issues")
