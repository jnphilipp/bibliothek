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

import sys

from bibliothek import stdout
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from typing import Dict, Optional, TextIO, Tuple, Type, TypeVar


class Link(models.Model):
    """Link ORM Model."""

    T = TypeVar("T", bound="Link", covariant=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    link = models.URLField(max_length=4096, unique=True, verbose_name=_("Link"))

    @classmethod
    def from_dict(cls: Type[T], data: Dict) -> Tuple[T, bool]:
        """Create a object from dict.

        Returns True if was crated, i. e. was not found in the DB.
        """
        return cls.objects.get_or_create(link=data["url"])

    @classmethod
    def get(cls: Type[T], term: str) -> Optional[T]:
        """Search DB for given term, return single object."""
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
    def search(cls: Type[T], term: str) -> models.query.QuerySet[T]:
        """Search DB for given term."""
        return cls.objects.filter(
            Q(pk=term if term.isdigit() else None) | Q(link__icontains=term)
        )

    def edit(self: T, field: str, value: str):
        """Change field by given value."""
        assert field in ["link", "url"]

        if field == "link" or field == "url":
            self.link = value
        self.save()

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

        ordering = ("link",)
        verbose_name = _("Link")
        verbose_name_plural = _("Links")
