# -*- coding: utf-8 -*-

import os
import shutil

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from journals.models import Journal
from languages.models import Language
from links.models import Link
from persons.models import Person


class TextFieldSingleLine(models.TextField):
    pass


class Paper(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    slug = models.SlugField(max_length=2048, unique=True, verbose_name=_('Slug'))
    title = TextFieldSingleLine(unique=True, verbose_name=_('Title'))
    authors = models.ManyToManyField(Person, related_name='papers', blank=True, verbose_name=_('Authors'))

    journal = models.ForeignKey(Journal, on_delete=models.SET_NULL, related_name='papers', blank=True, null=True, verbose_name=_('Journal'))
    volume = TextFieldSingleLine(blank=True, null=True, verbose_name=_('Volume'))
    published_on = models.DateField(blank=True, null=True, verbose_name=_('Published on'))
    languages = models.ManyToManyField(Language, related_name='papers', blank=True, verbose_name=_('Languages'))

    files = GenericRelation('files.File', verbose_name=_('Files'))
    bibtex = models.TextField(blank=True, null=True, verbose_name=_('BibTex'))

    links = models.ManyToManyField(Link, related_name='papers', blank=True, verbose_name=_('Links'))

    acquisitions = GenericRelation('shelves.Acquisition', verbose_name=_('Acquisitions'))
    reads = GenericRelation('shelves.Read', verbose_name=_('Reads'))

    def move_file(self, file):
        save_name = os.path.join('papers', str(self.id), os.path.basename(file.file.name))

        current_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
        new_path = os.path.join(settings.MEDIA_ROOT, save_name)

        if os.path.exists(current_path) and current_path != new_path:
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            shutil.move(current_path, new_path)
            file.file.name = save_name
            file.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        else:
            orig = Paper.objects.get(pk=self.id)
            if orig.title != self.title:
                self.slug = slugify(self.title)
        super(Paper, self).save(*args, **kwargs)
        for file in self.files.all():
            if not file.file.name.startswith(os.path.join('papers', str(self.id))):
                self.move_file(file)

    def to_json(self):
        data = {'title': self.title}
        if self.authors.all():
            data['authors'] = [author.to_json() for author in self.authors.all()]
        if self.journal:
            data['journal'] = self.journal.to_json()
        if self.volume:
            data['volume'] = self.volume
        if self.published_on:
            data['published_on'] = str(self.published_on)
        if self.languages.all():
            data['languages'] = [language.to_json() for language in self.languages.all()]
        if self.links.all():
            data['links'] = [link.to_json() for link in self.links.all()]
        if self.files.all():
            data['files'] = [file.to_json() for file in self.files.all()]
        if self.acquisitions.all():
            data['acquisitions'] = [acquisition.to_json() for acquisition in self.acquisitions.all()]
        if self.reads.all():
            data['reads'] = [read.to_json() for read in self.reads.all()]
        return data

    def __str__(self):
        return '%s%s' % (self.title, '' if self.authors.count() == 0 else ' - %s' % ', '.join([str(a) for a in self.authors.all()]))

    class Meta:
        ordering = ('journal__name', 'volume', 'title')
        unique_together = ('journal', 'volume')
        verbose_name = _('Paper')
        verbose_name_plural = _('Papers')
