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
"""Shelves Django app models."""

import datetime
import sys

from bibliothek import stdout
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _
from typing import Dict, Optional, TextIO, Tuple, Type, TypeVar, Union


class Acquisition(models.Model):
    """Acquisition ORM Model."""

    T = TypeVar("T", bound="Acquisition", covariant=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    date = models.DateField(blank=True, null=True, verbose_name=_("Date"))
    price = models.FloatField(default=0, verbose_name=_("Price"))

    content_type = models.ForeignKey(ContentType, models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    @classmethod
    def from_dict(
        cls: Type[T], data: Dict, content_object: models.Model
    ) -> Tuple[T, bool]:
        """Create from dict.

        Returns True if was crated, i. e. was not found in the DB.
        """
        date = None
        if "date" in data and data["date"]:
            if type(data["date"]) == str:
                date = datetime.datetime.strptime(data["date"], "%Y-%m-%d").date()
            elif type(data["date"]) == datetime.date:
                date = data["date"]
        return cls.objects.get_or_create(
            date=date,
            price=data["price"] if "price" in data else 0,
            content_type=ContentType.objects.get_for_model(content_object),
            object_id=content_object.pk,
        )

    @classmethod
    def get(
        cls: Type[T],
        term: str,
        **kwargs,
    ) -> Optional[T]:
        """Search for given term, return single object."""
        query_set = cls.search(term, **kwargs)
        if query_set.count() == 0:
            return None
        elif query_set.count() > 1:
            if term.isdigit():
                query_set = query_set.filter(pk=term)
            else:
                query_set = query_set.filter(
                    Q(ni=term)
                    | Q(jv=term)
                    | Q(editions__isbn=term)
                    | Q(editions__book__title=term)
                    | Q(papers__title=term)
                    | Q(editions__alternate_title=term)
                )
            if query_set.count() != 1:
                return None
        return query_set[0]

    @classmethod
    def search(
        cls: Type[T],
        term: str,
        **kwargs,
    ) -> models.query.QuerySet[T]:
        """Search for given term."""
        if kwargs:
            return cls.objects.filter(**kwargs).filter(
                pk=term if term.isdigit() else None
            )
        return (
            cls.objects.annotate(
                jv=Concat(
                    "papers__journal__name",
                    Value(" "),
                    "papers__volume",
                    output_field=models.TextField(),
                ),
                ni=Concat(
                    "issues__magazine__name",
                    Value(" "),
                    "issues__issue",
                    output_field=models.TextField(),
                ),
            )
            .filter(
                Q(pk=term if term.isdigit() else None)
                | Q(editions__alternate_title__icontains=term)
                | Q(editions__isbn__icontains=term)
                | Q(jv__icontains=term)
                | Q(ni__iregex=term.replace(" ", ".*?"))
                | Q(papers__title__icontains=term)
                | Q(editions__book__title__icontains=term)
            )
            .distinct()
        )

    def edit(self: T, field: str, value: Union[float, datetime.date], *args, **kwargs):
        """Change field by given value."""
        assert field in ["date", "price"]

        if field == "date":
            self.date = value
        elif field == "price":
            self.price = value
        self.save(*args, **kwargs)

    def print(self: T, file: TextIO = sys.stdout):
        """Print instance info."""
        stdout.write([_("Field"), _("Value")], "=", [0.33], file=file)
        stdout.write([_("Id"), self.id], positions=[0.33], file=file)
        stdout.write(
            [_("Obj"), f"{self.content_object.pk}: {self.content_object}"],
            positions=[0.33],
            file=file,
        )
        stdout.write([_("Date"), self.date], positions=[0.33], file=file)
        stdout.write([_("Price"), self.price], positions=[0.33], file=file)

    def to_dict(self: T) -> Dict:
        """Convert to dict."""
        return {
            "date": self.date.strftime("%Y-%m-%d") if self.date else None,
            "price": self.price,
        }

    def __str__(self):
        """Name."""
        return f'Acquisition "{self.content_object}" [{self.date} - {self.price}]'

    class Meta:
        """Meta."""

        ordering = ("date",)
        verbose_name = _("Acquisition")
        verbose_name_plural = _("Acquisitions")


class Read(models.Model):
    """Read ORM Model."""

    T = TypeVar("T", bound="Read", covariant=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    started = models.DateField(blank=True, null=True, verbose_name=_("Started"))
    finished = models.DateField(blank=True, null=True, verbose_name=_("Finished"))

    content_type = models.ForeignKey(ContentType, models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    @classmethod
    def from_dict(
        cls: Type[T], data: Dict, content_object: models.Model
    ) -> Tuple[T, bool]:
        """Create from dict.

        Returns True if was crated, i. e. was not found in the DB.
        """
        started = None
        if "started" in data and data["started"]:
            if type(data["started"]) == str:
                started = datetime.datetime.strptime(data["started"], "%Y-%m-%d").date()
            elif type(data["started"]) == datetime.date:
                started = data["started"]
        finished = None
        if "finished" in data and data["finished"]:
            if type(data["finished"]) == str:
                finished = datetime.datetime.strptime(
                    data["finished"], "%Y-%m-%d"
                ).date()
            elif type(data["finished"]) == datetime.date:
                finished = data["finished"]

        return cls.objects.get_or_create(
            started=started,
            finished=finished,
            content_type=ContentType.objects.get_for_model(content_object),
            object_id=content_object.pk,
        )

    @classmethod
    def get(cls: Type[T], term: str, **kwargs) -> Optional[T]:
        """Search for given term, return single object."""
        query_set = cls.search(term, **kwargs)
        if query_set.count() == 0:
            return None
        elif query_set.count() > 1:
            if term.isdigit():
                query_set = query_set.filter(pk=term)
            else:
                query_set = query_set.filter(
                    Q(editions__alternate_title=term)
                    | Q(editions__isbn=term)
                    | Q(ni=term)
                    | Q(editions__book__title=term)
                    | Q(jv=term)
                    | Q(papers__title=term)
                )
            if query_set.count() != 1:
                return None
        return query_set[0]

    @classmethod
    def search(cls: Type[T], term: str, **kwargs) -> models.query.QuerySet[T]:
        """Search for given term."""
        if kwargs:
            return cls.objects.filter(**kwargs).filter(
                pk=term if term.isdigit() else None
            )
        return (
            cls.objects.annotate(
                jv=Concat(
                    "papers__journal__name",
                    Value(" "),
                    "papers__volume",
                    output_field=models.TextField(),
                ),
                ni=Concat(
                    "issues__magazine__name",
                    Value(" "),
                    "issues__issue",
                    output_field=models.TextField(),
                ),
            )
            .filter(
                Q(pk=term if term.isdigit() else None)
                | Q(editions__alternate_title__icontains=term)
                | Q(editions__isbn__icontains=term)
                | Q(jv__icontains=term)
                | Q(ni__iregex=term.replace(" ", ".*?"))
                | Q(papers__title__icontains=term)
                | Q(editions__book__title__icontains=term)
            )
            .distinct()
        )

    def edit(self: T, field: str, value: datetime.date, *args, **kwargs):
        """Change field by given value."""
        assert field in ["started", "finished"]

        if field == "started":
            self.started = value
        elif field == "finished":
            self.finished = value
        self.save(*args, **kwargs)

    def print(self: T, file: TextIO = sys.stdout):
        """Print instance info."""
        stdout.write([_("Field"), _("Value")], "=", [0.33], file=file)
        stdout.write([_("Id"), self.id], positions=[0.33], file=file)
        stdout.write(
            [_("Obj"), f"{self.content_object.pk}: {self.content_object}"],
            positions=[0.33],
            file=file,
        )
        stdout.write([_("Started"), self.started], positions=[0.33], file=file)
        stdout.write([_("Finished"), self.finished], positions=[0.33], file=file)

    def to_dict(self: T) -> Dict:
        """Convert to dict."""
        return {
            "started": self.started.strftime("%Y-%m-%d") if self.started else None,
            "finished": self.finished.strftime("%Y-%m-%d") if self.finished else None,
        }

    def __str__(self):
        """Name."""
        return f'Read "{self.content_object}" [{self.started} - {self.finished}]'

    class Meta:
        """Meta."""

        ordering = ("started", "finished")
        verbose_name = _("Read")
        verbose_name_plural = _("Reads")
