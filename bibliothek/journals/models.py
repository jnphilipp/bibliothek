# -*- coding: utf-8 -*-

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from links.models import Link


class TextFieldSingleLine(models.TextField):
    pass


class Journal(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    slug = models.SlugField(max_length=2048, unique=True, verbose_name=_('Slug'))
    name = TextFieldSingleLine(unique=True, verbose_name=_('Name'))
    links = models.ManyToManyField(Link, related_name='journals', blank=True, verbose_name=_('Links'))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            orig = Journal.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(self.name)
        super(Journal, self).save(*args, **kwargs)

    def to_json(self):
        return {'name': self.name}

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _('Journal')
        verbose_name_plural = _('Journals')
