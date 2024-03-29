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
"""Links Django app models."""

import sys

from bibliothek import stdout
from django.db import models
from django.db.models import F, Func, Q
from django.utils.translation import gettext_lazy as _
from typing import Dict, Optional, TextIO, Tuple, Type, TypeVar


class Link(models.Model):
    """Link Model."""

    T = TypeVar("T", bound="Link", covariant=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    link = models.URLField(max_length=4096, unique=True, verbose_name=_("Link"))

    @classmethod
    def from_dict(cls: Type[T], data: Dict) -> Tuple[T, bool]:
        """Create from dict.

        Returns True if was crated, i. e. was not found in the DB.
        """
        return cls.objects.get_or_create(link=data["url"])

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
                query_set = query_set.filter(link=term)
            if query_set.count() != 1:
                return None
        return query_set[0]

    @classmethod
    def get_or_create(cls: Type[T], term: str) -> T:
        """Search for given term and if not found create it, return single object."""
        obj = cls.get(term)
        if obj is None:
            return cls.from_dict({"url": term})[0]
        return obj

    @classmethod
    def search(cls: Type[T], term: str) -> models.query.QuerySet[T]:
        """Search for given term."""
        return cls.objects.filter(
            Q(pk=term if term.isdigit() else None) | Q(link__icontains=term)
        )

    def edit(self: T, field: str, value: str):
        """Change field by given value."""
        assert field in ["link", "url"]

        if field == "link" or field == "url":
            self.link = value
        self.save()

    def num_related(self: T, exclude: Optional[str] = None) -> int:
        """Get number of related objects."""
        return sum(
            [
                getattr(self, rel.name).count()
                for rel in self._meta.related_objects
                if rel.name != exclude
            ]
        )

    def print(self: T, file: TextIO = sys.stdout):
        """Print instance info."""
        stdout.write([_("Field"), _("Value")], "=", [0.33], file=file)
        stdout.write([_("Id"), self.id], positions=[0.33], file=file)
        stdout.write([_("URL"), self.link], positions=[0.33], file=file)

    def to_dict(self: T) -> Dict:
        """Convert to dict."""
        return {"url": self.link}

    def __str__(self: T) -> str:
        """Name."""
        return self.link

    class Meta:
        """Meta."""

        ordering = (Func(F("link"), function="LOWER"),)
        verbose_name = _("Link")
        verbose_name_plural = _("Links")
