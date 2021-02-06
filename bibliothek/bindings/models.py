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
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from typing import Dict, Optional, TextIO, Tuple, Type, TypeVar


class Binding(models.Model):
    """Binding ORM Model."""

    T = TypeVar("T", bound="Binding", covariant=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    slug = models.SlugField(max_length=2048, unique=True, verbose_name=_("Slug"))
    name = models.TextField(unique=True, verbose_name=_("Name"))

    @classmethod
    def from_dict(cls: Type[T], data: Dict) -> Tuple[T, bool]:
        """Create a object from dict.

        Returns True if was crated, i. e. was not found in the DB.
        """
        return cls.objects.get_or_create(name=data["name"])

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
                query_set = query_set.filter(name=term)
            if query_set.count() != 1:
                return None
        return query_set[0]

    @classmethod
    def search(cls: Type[T], term: str) -> models.query.QuerySet[T]:
        """Search DB for given term."""
        return cls.objects.filter(
            Q(pk=term if term.isdigit() else None) | Q(name__icontains=term)
        )

    def edit(self: T, field: str, value: str):
        """Change field by given value."""
        assert field in ["name"]

        if field == "name":
            self.name = value
        self.save()

    def print(self: T, file: TextIO = sys.stdout):
        """Print instance info."""
        positions = [0.33]
        stdout.write([_("Field"), _("Value")], "=", positions, file=file)
        stdout.write([_("Id"), self.id], positions=positions, file=file)
        stdout.write([_("Name"), self.name], positions=positions, file=file)

    def save(self: T, *args, **kwargs):
        """Save in DB."""
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            orig = Binding.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(self.name)
        super(Binding, self).save(*args, **kwargs)

    def to_dict(self: T) -> Dict:
        """Convert to dict."""
        return {"name": self.name}

    def __str__(self: T) -> str:
        """Name."""
        return self.name

    class Meta:
        """Meta."""

        ordering = ("name",)
        verbose_name = _("Binding")
        verbose_name_plural = _("Bindings")
