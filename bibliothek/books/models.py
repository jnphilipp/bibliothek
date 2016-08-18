# -*- coding: utf-8 -*-

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from links.models import Link
from persons.models import Person
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
