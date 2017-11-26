# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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
import shutil

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from languages.models import Language
from links.models import Link


class SingleLineTextField(models.TextField):
    pass


class Magazine(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    slug = models.SlugField(
        max_length=2048,
        unique=True,
        verbose_name=_('Slug')
    )
    name = SingleLineTextField(
        unique=True,
        verbose_name=_('Name')
    )

    feed = models.ForeignKey(
        Link,
        models.CASCADE,
        related_name='magazine_feed',
        blank=True,
        null=True,
        verbose_name=_('Feed')
    )
    links = models.ManyToManyField(
        Link,
        blank=True,
        related_name='magazines',
        verbose_name=_('Links')
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            orig = Magazine.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(self.name)
        super(Magazine, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _('Magazine')
        verbose_name_plural = _('Magazines')


class Issue(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    issue = SingleLineTextField(
        verbose_name=_('Issue')
    )
    magazine = models.ForeignKey(
        Magazine,
        models.CASCADE,
        related_name='issues',
        verbose_name=_('Magazine')
    )
    publishing_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Publishing date')
    )
    languages = models.ManyToManyField(
        Language,
        blank=True,
        related_name='issues',
        verbose_name=_('Languages')
    )

    files = GenericRelation(
        'files.File',
        verbose_name=_('Files')
    )
    cover_image = models.ImageField(
        upload_to='files',
        blank=True,
        null=True,
        verbose_name=_('Cover image')
    )
    links = models.ManyToManyField(
        Link,
        blank=True,
        related_name='issues',
        verbose_name=_('Links')
    )

    acquisitions = GenericRelation(
        'shelves.Acquisition',
        verbose_name=_('Acquisitions')
    )
    reads = GenericRelation(
        'shelves.Read',
        verbose_name=_('Reads')
    )

    def move_file(self, file):
        save_name = os.path.join('magazines', str(self.magazine.id),
                                 str(self.id),
                                 os.path.basename(file.file.name))

        current_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
        new_path = os.path.join(settings.MEDIA_ROOT, save_name)

        if os.path.exists(current_path) and current_path != new_path:
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            shutil.move(current_path, new_path)
            file.file.name = save_name
            file.save()

    def move_cover_image(self):
        save_name = os.path.join(
            'magazines',
            str(self.magazine.id),
            str(self.id),
            'cover%s' % os.path.splitext(self.cover_image.name)[1]
        )

        current_path = os.path.join(settings.MEDIA_ROOT, self.cover_image.name)
        new_path = os.path.join(settings.MEDIA_ROOT, save_name)

        if os.path.exists(current_path) and current_path != new_path:
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            shutil.move(current_path, new_path)
            self.cover_image.name = save_name

    def save(self, *args, **kwargs):
        if self.cover_image and \
                not self.cover_image.name.startswith('magazines'):
            self.move_cover_image()
        super(Issue, self).save(*args, **kwargs)
        for file in self.files.all():
            path = os.path.join('magazines', str(self.id))
            if not file.file.name.startswith(path):
                self.move_file(file)

    def __str__(self):
        return '%s %s' % (self.magazine.name, self.issue)

    class Meta:
        ordering = ('magazine', 'issue')
        unique_together = ('magazine', 'issue')
        verbose_name = _('Issue')
        verbose_name_plural = _('Issues')
