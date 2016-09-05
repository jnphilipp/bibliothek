# -*- coding: utf-8 -*-

import os
import shutil

from bindings.models import Binding
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from genres.models import Genre
from languages.models import Language
from links.models import Link
from persons.models import Person
from publishers.models import Publisher
from series.models import Series


class TextFieldSingleLine(models.TextField):
    pass


class Book(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    slug = models.SlugField(max_length=2048, unique=True)
    title = TextFieldSingleLine(unique=True)
    authors = models.ManyToManyField(Person, related_name='books', blank=True)

    series = models.ForeignKey(Series, on_delete=models.SET_NULL, related_name='books', blank=True, null=True)
    volume = models.FloatField(default=0, blank=True)

    genres = models.ManyToManyField(Genre, related_name='books', blank=True)
    links = models.ManyToManyField(Link, related_name='books', blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        else:
            orig = Book.objects.get(pk=self.id)
            if orig.title != self.title:
                self.slug = slugify(self.title)
        super(Book, self).save(*args, **kwargs)


    def to_json(self):
        data = {'title':self.title}
        if self.authors.all():
            data['authors'] = [author.to_json() for author in self.authors.all()]
        if self.series:
            data['series'] = self.series.name
            data['volume'] = self.volume
        return data


    def __str__(self):
        return '%s%s%s' % (self.title, '' if self.authors.count() == 0 else ' - %s' % ', '.join([str(a) for a in self.authors.all()]), ' (%s #%g)' % (self.series, self.volume) if self.series else '')


    class Meta:
        ordering = ('authors__last_name', 'authors__first_name', 'series', 'volume', 'title')
        verbose_name = _('Book')
        verbose_name_plural = _('Books')


class Edition(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    book = models.ForeignKey(Book, related_name='editions')
    isbn = models.CharField(max_length=13, blank=True, null=True)
    published_on = models.DateField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='files', blank=True, null=True)
    files = GenericRelation('files.File')

    publisher = models.ForeignKey(Publisher, related_name='editions', blank=True, null=True)
    binding = models.ForeignKey(Binding, related_name='editions', blank=True, null=True)
    languages = models.ManyToManyField(Language, related_name='editions', blank=True)
    bibtex = models.TextField(blank=True, null=True)

    acquisitions = GenericRelation('shelves.Acquisition')
    reads = GenericRelation('shelves.Read')


    def move_file(self, file):
        save_name = os.path.join('books', str(self.book.id), str(self.id), os.path.basename(file.file.name))

        current_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
        new_path = os.path.join(settings.MEDIA_ROOT, save_name)

        if os.path.exists(current_path) and current_path != new_path:
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            shutil.move(current_path, new_path)
            file.file.name = save_name
            file.save()


    def move_cover_image(self):
        save_name = os.path.join('books', str(self.book.id), str(self.id), 'cover%s' % os.path.splitext(self.cover_image.name)[1])

        current_path = os.path.join(settings.MEDIA_ROOT, self.cover_image.name)
        new_path = os.path.join(settings.MEDIA_ROOT, save_name)

        if os.path.exists(current_path) and current_path != new_path:
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            shutil.move(current_path, new_path)
            self.cover_image.name = save_name


    def save(self, *args, **kwargs):
        if self.cover_image and not 'books' in self.cover_image.name:
            self.move_cover_image()
        super(Edition, self).save(*args, **kwargs)
        for file in self.files.all():
            if not 'books' in file.file:
                self.move_file(file)


    def __str__(self):
        return '%s #%s' % (self.book, self.id)


    class Meta:
        ordering = ('book', 'published_on')
        verbose_name = _('Edition')
        verbose_name_plural = _('Editions')
