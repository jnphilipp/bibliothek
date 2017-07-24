# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Link(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    link = models.URLField(max_length=4096, unique=True, verbose_name=_('Link'))

    def to_json(self):
        return {'link': self.link}

    def __str__(self):
        return self.link

    class Meta:
        ordering = ('link',)
        verbose_name = _('Link')
        verbose_name_plural = _('Links')
