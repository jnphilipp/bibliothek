# -*- coding: utf-8 -*-

from django.db import models
from django.template.defaultfilters import slugify
from links.models import Link


class TextFieldSingleLine(models.TextField):
    pass


class Publisher(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    slug = models.SlugField(max_length=2048, unique=True)
    name = TextFieldSingleLine(unique=True)
    links = models.ManyToManyField(Link, related_name='publishers', blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            orig = Publisher.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(self.name)
        super(Publisher, self).save(*args, **kwargs)


    def __str__(self):
        return self.name


    class Meta:
        ordering = ('name',)
