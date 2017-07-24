# -*- coding: utf-8 -*-

import os

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class File(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    file = models.FileField(upload_to='files', max_length=4096, verbose_name=_('File'))

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def to_json(self):
        return {'file_name': os.path.basename(self.file.name)}

    def __str__(self):
        return os.path.basename(self.file.name)

    class Meta:
        ordering = ('file',)
        verbose_name = _('File')
        verbose_name_plural = _('Files')
