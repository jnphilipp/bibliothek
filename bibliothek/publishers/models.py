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
"""Publishers Django app models."""

import sys

from bibliothek import stdout
from bibliothek.utils import concat, lookahead
from django.db import models
from django.db.models import F, Func, Q
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from links.models import Link
from typing import Dict, Optional, TextIO, Tuple, Type, TypeVar


class Publisher(models.Model):
    """Publisher Model."""

    T = TypeVar("T", bound="Publisher", covariant=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    slug = models.SlugField(max_length=2048, unique=True, verbose_name=_("Slug"))
    name = models.TextField(unique=True, verbose_name=_("Name"))
    links = models.ManyToManyField(
        Link, related_name="publishers", blank=True, verbose_name=_("Links")
    )

    @classmethod
    def from_dict(cls: Type[T], data: Dict) -> Tuple[T, bool]:
        """Create from dict.

        Returns True if was crated, i. e. was not found in the DB.
        """
        publisher, created = cls.objects.get_or_create(name=data["name"])

        for i in data["links"] if "links" in data and data["links"] else []:
            publisher.links.add(Link.from_dict(i)[0])

        return publisher, created

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
                query_set = query_set.filter(name=term)
            if query_set.count() != 1:
                return None
        return query_set[0]

    @classmethod
    def get_or_create(cls: Type[T], term: str) -> T:
        """Search for given term and if not found create it, return single object."""
        obj = cls.get(term)
        if obj is None:
            return cls.from_dict({"name": term})[0]
        return obj

    @classmethod
    def search(cls: Type[T], term: str) -> models.query.QuerySet[T]:
        """Search for given term."""
        return cls.objects.filter(
            Q(pk=term if term.isdigit() else None) | Q(name__icontains=term)
        )

    def delete(self: T) -> Tuple[int, Dict[str, int]]:
        """Delete."""
        deleted: Tuple[int, Dict[str, int]] = (0, dict())
        for link in self.links.all():
            if link.num_related("publishers") == 0:
                deleted = concat(deleted, link.delete())
        return concat(deleted, super(Publisher, self).delete())

    def edit(self: T, field: str, value: str, *args, **kwargs):
        """Change field by given value."""
        assert field in ["name", "link"]

        if field == "name":
            self.name = value
        elif field == "link":
            link = Link.get_or_create(value)
            if self.links.filter(pk=link.pk).exists():
                self.links.remove(link)
            else:
                self.links.add(link)
        self.save(*args, **kwargs)

    def print(self: T, file: TextIO = sys.stdout):
        """Print info."""
        stdout.write([_("Field"), _("Value")], "=", [0.33], file=file)
        stdout.write([_("Id"), self.id], positions=[0.33], file=file)
        stdout.write([_("Name"), self.name], positions=[0.33], file=file)

        if self.links.count() > 0:
            for (i, link), has_next in lookahead(enumerate(self.links.all())):
                stdout.write(
                    [_("Links") if i == 0 else "", f"{link.id}: {link.link}"],
                    "" if has_next else "_",
                    [0.33],
                    file=file,
                )
        else:
            stdout.write(f"{_('Links')}", file=file)

        if self.editions.count() > 0:
            editions = self.editions.all().order_by("publishing_date")
            for (i, edition), has_next in lookahead(enumerate(editions)):
                stdout.write(
                    [_("Editions") if i == 0 else "", f"{edition.id}: {edition}"],
                    "" if has_next else "_",
                    [0.33],
                    file=file,
                )
        else:
            stdout.write(f"{_('Editions')}", file=file)

    def save(self: T, *args, **kwargs):
        """Save."""
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            orig = Publisher.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(self.name)
        super(Publisher, self).save(*args, **kwargs)

    def to_dict(self: T) -> Dict:
        """Convert to dict."""
        return {
            "name": self.name,
            "links": [i.to_dict() for i in self.links.all()]
            if self.links.count() > 0
            else None,
        }

    def __str__(self: T) -> str:
        """Name."""
        return self.name

    class Meta:
        """Meta."""

        ordering = (Func(F("name"), function="LOWER"),)
        verbose_name = _("Publisher")
        verbose_name_plural = _("Publishers")
