# -*- coding: utf-8 -*-

import os
import shutil

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.defaultfilters import slugify
from journals.models import Journal
from languages.models import Language
from links.models import Link
from persons.models import Person


class TextFieldSingleLine(models.TextField):
    pass


class Paper(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    slug = models.SlugField(max_length=2048, unique=True)
    title = TextFieldSingleLine(unique=True)
    authors = models.ManyToManyField(Person, related_name='papers', blank=True)

    journal = models.ForeignKey(Journal, on_delete=models.SET_NULL, related_name='papers', blank=True, null=True)
    volume = TextFieldSingleLine(blank=True, null=True)
    published_on = models.DateField(blank=True, null=True)
    languages = models.ManyToManyField(Language, related_name='papers', blank=True)

    files = GenericRelation('files.File')
    bibtex = models.TextField(blank=True, null=True)

    links = models.ManyToManyField(Link, related_name='papers', blank=True)


    def move_file(self, file):
        name = slugify('%s%s' % (self.title, '' if self.authors.count() == 0 else ' - %s' % ', '.join([str(a) for a in self.authors.all()])))
        save_name = os.path.join('papers', str(self.id), name + os.path.splitext(os.path.basename(file.file.name))[1])

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
            if not 'papers' in file.file:
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
        return data


    def __str__(self):
        return '%s%s' % (self.title, '' if self.authors.count() == 0 else ' - %s' % ', '.join([str(a) for a in self.authors.all()]))


    class Meta:
        ordering = ('journal__name', 'volume', 'title')
        unique_together = ('journal', 'volume')
        verbose_name = ' paper'
