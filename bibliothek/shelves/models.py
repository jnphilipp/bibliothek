# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Acquisition(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date')
    )
    price = models.FloatField(
        default=0,
        verbose_name=_('Price')
    )

    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

    def to_json(self):
        return {'date': str(self.date), 'price': str(self.price)}

    def __str__(self):
        return 'Acquisition "%s"' % self.content_object

    class Meta:
        ordering = ('date',)
        verbose_name = _('Acquisition')
        verbose_name_plural = _('Acquisitions')


class Read(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    started = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date started')
    )
    finished = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date finished')
    )

    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

    def to_json(self):
        return {'started': str(self.started), 'finished': str(self.finished)}

    def __str__(self):
        return 'Read "%s"' % self.content_object

    class Meta:
        ordering = ('started', 'finished')
        verbose_name = _('Read')
        verbose_name_plural = _('Reads')
