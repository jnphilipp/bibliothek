# -*- coding: utf-8 -*-

from django.db import models
from django.template.defaultfilters import slugify
from links.models import Link


class TextFieldSingleLine(models.TextField):
    pass


class Magazine(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    slug = models.SlugField(max_length=2048, unique=True)
    name = TextFieldSingleLine(unique=True)

    links = models.ManyToManyField(Link, related_name='magazines', blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            orig = Magazine.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(self.name)
        super(Magazine, self).save(*args, **kwargs)


    def __str__(self):
        return self.name


    class Meta:
        ordering = ('name',)
