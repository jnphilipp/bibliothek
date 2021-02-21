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
"""Files app models."""

import os

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files import File as DJFile
from django.db import models
from django.utils.translation import ugettext_lazy as _
from typing import Dict, Tuple, Type, TypeVar


class File(models.Model):
    """File ORM Model."""

    T = TypeVar("T", bound="File", covariant=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    file = models.FileField(upload_to="files", max_length=4096, verbose_name=_("File"))
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, blank=True, null=True
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    @classmethod
    def from_dict(
        cls: Type[T], data: Dict, content_object: models.Model = None
    ) -> Tuple[T, bool]:
        """Create from dict.

        Returns True if was crated, i. e. was not found in the DB.
        """
        try:
            args = {}
            if content_object:
                args["content_type"] = ContentType.objects.get_for_model(content_object)
                args["object_id"] = content_object.pk
            path = data["path"].replace(str(settings.MEDIA_ROOT), "")
            return (
                cls.objects.get(
                    file=path[1:] if path.startswith("/") else path, **args
                ),
                False,
            )
        except cls.DoesNotExist:
            file = cls()
            file.file.save(
                os.path.basename(data["path"]), DJFile(open(data["path"], "rb"))
            )
            file.content_object = content_object
            file.save()
            return file, True

    def to_dict(self: T) -> Dict:
        """Convert to dict."""
        return {"path": self.file.path}

    def __str__(self: T) -> str:
        """Name."""
        return os.path.basename(self.file.name)

    class Meta:
        """Meta."""

        ordering = ("file",)
        verbose_name = _("File")
        verbose_name_plural = _("Files")
