# -*- coding: utf-8 -*-

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Acquisition(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    date = models.DateField(blank=True, null=True, verbose_name=_('Date'))
    price = models.FloatField(default=0, verbose_name=_('Price'))

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def to_json(self):
        return {'date': str(self.date), 'price': str(self.price)}

    def __str__(self):
        return 'Acquisition "%s"' % self.content_object

    class Meta:
        ordering = ('date',)
        verbose_name = _('Acquisition')
        verbose_name_plural = _('Acquisitions')


class Read(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    started = models.DateField(blank=True, null=True, verbose_name=_('Date started'))
    finished = models.DateField(blank=True, null=True, verbose_name=_('Date finished'))

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def to_json(self):
        return {'started': str(self.started), 'finished': str(self.finished)}

    def __str__(self):
        return 'Read "%s"' % self.content_object

    class Meta:
        ordering = ('started', 'finished')
        verbose_name = _('Read')
        verbose_name_plural = _('Reads')
