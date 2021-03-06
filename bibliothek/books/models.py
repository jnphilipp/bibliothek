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

import hashlib
import os
import shutil

from bibliothek.fields import SingleLineTextField
from bindings.models import Binding
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from genres.models import Genre
from languages.models import Language
from links.models import Link
from persons.models import Person
from publishers.models import Publisher
from series.models import Series


class Book(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_('Updated at'))

    slug = models.SlugField(max_length=2048, unique=True,
                            verbose_name=_('Slug'))
    title = SingleLineTextField(unique=True, verbose_name=_('Title'))
    authors = models.ManyToManyField(Person, blank=True, related_name='books',
                                     verbose_name=_('Authors'))

    series = models.ForeignKey(Series, models.SET_NULL, blank=True, null=True,
                               related_name='books', verbose_name=_('Series'))
    volume = models.FloatField(default=0, blank=True, verbose_name=_('Volume'))

    genres = models.ManyToManyField(Genre, blank=True, related_name='books',
                                    verbose_name=_('Genres'))
    links = models.ManyToManyField(Link, blank=True, related_name='books',
                                   verbose_name=_('Links'))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        else:
            orig = Book.objects.get(pk=self.id)
            if orig.title != self.title:
                self.slug = slugify(self.title)
        if self.slug is None or self.slug == '':
            self.slug = hashlib.md5(self.title.encode('utf8')).hexdigest()
        super(Book, self).save(*args, **kwargs)

    def to_json(self):
        data = {
            'title': self.title,
            'authors': [a.to_json() for a in self.authors.all()],
            'genres': [g.to_json() for g in self.genres.all()],
            'links': [l.to_json() for l in self.links.all()]
        }
        if self.series:
            data['series'] = self.series.name
            data['volume'] = self.volume
        return data

    def __str__(self):
        authors = ', '.join([f'{a}' for a in self.authors.all()])
        authors = '' if self.authors.count() == 0 else f' - {authors}'
        series = f' ({self.series} #{self.volume:g})' if self.series else ''
        return f'{self.title}{authors}{series}'

    class Meta:
        ordering = ('series', 'volume', 'title')
        verbose_name = _('Book')
        verbose_name_plural = _('Books')


class Edition(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_('Updated at'))

    alternate_title = SingleLineTextField(blank=True, null=True,
                                          verbose_name=_('Alternate title'))
    book = models.ForeignKey(Book, models.CASCADE, related_name='editions',
                             verbose_name=_('Book'))
    isbn = models.CharField(max_length=13, blank=True, null=True,
                            verbose_name=_('ISBN'))
    publishing_date = models.DateField(blank=True, null=True,
                                       verbose_name=_('Publishing date'))
    cover_image = models.ImageField(upload_to='files', blank=True, null=True,
                                    verbose_name=_('Cover image'))
    files = GenericRelation('files.File', verbose_name=_('Files'))

    publisher = models.ForeignKey(Publisher, models.SET_NULL, blank=True,
                                  null=True, related_name='editions',
                                  verbose_name=_('Publisher'))
    binding = models.ForeignKey(Binding, models.SET_NULL, blank=True,
                                null=True, related_name='editions',
                                verbose_name=_('Binding'))
    languages = models.ManyToManyField(Language, blank=True,
                                       related_name='editions',
                                       verbose_name=_('Languages'))
    links = models.ManyToManyField(Link, blank=True, related_name='editions',
                                   verbose_name=_('Links'))
    bibtex = models.TextField(blank=True, null=True, verbose_name=_('BibTex'))
    persons = models.ManyToManyField(Person, blank=True,
                                     related_name='editions',
                                     verbose_name=_('Persons'))

    acquisitions = GenericRelation('shelves.Acquisition',
                                   verbose_name=_('Acquisitions'))
    reads = GenericRelation('shelves.Read', related_query_name='editions',
                            verbose_name=_('Reads'))

    def get_title(self):
        if self.alternate_title:
            return self.alternate_title
        else:
            return self.book.title

    def move_file(self, file):
        save_name = os.path.join('books', str(self.book.id), str(self.id),
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
        ending = os.path.splitext(self.cover_image.name)[1]
        save_name = os.path.join('books', str(self.book.id), str(self.id),
                                 f'cover{ending}')

        current_path = os.path.join(settings.MEDIA_ROOT, self.cover_image.name)
        new_path = os.path.join(settings.MEDIA_ROOT, save_name)

        if os.path.exists(current_path) and current_path != new_path:
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            shutil.move(current_path, new_path)
            self.cover_image.name = save_name

    def save(self, *args, **kwargs):
        path = os.path.join('books', str(self.book.id), str(self.id))
        if self.cover_image and not self.cover_image.name.startswith(path):
            self.move_cover_image()
        super(Edition, self).save(*args, **kwargs)
        for file in self.files.all():
            if not file.file.name.startswith(path):
                self.move_file(file)

    def __str__(self):
        authors = ', '.join([f'{a}' for a in self.book.authors.all()])
        authors = '' if self.book.authors.count() == 0 else f' - {authors}'
        series = ''
        if self.book.series:
            series = f' ({self.book.series} #{self.book.volume:g})'
        return f'{self.get_title()}{authors}{series} #{self.id}'

    class Meta:
        ordering = ('book', 'publishing_date')
        verbose_name = _('Edition')
        verbose_name_plural = _('Editions')
