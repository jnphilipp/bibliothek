# -*- coding: utf-8 -*-

from django.db import models
from django.template.defaultfilters import slugify
from links.models import Link


class TextFieldSingleLine(models.TextField):
    pass


class Person(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    slug = models.SlugField(max_length=2048, unique=True)
    first_name = TextFieldSingleLine()
    last_name = TextFieldSingleLine(blank=True, null=True)
    links = models.ManyToManyField(Link, related_name='persons', blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            s = slugify('%s_%s' % (self.first_name, self.last_name))
            if Person.objects.filter(slug=s).exists():
                self.slug = slugify('%s_%s_%s' % (self.id, self.first_name, self.last_name))
            else:
                self.slug = s
        else:
            orig = Person.objects.get(pk=self.id)
            if orig.first_name != self.first_name or orig.last_name != self.last_name:
                s = slugify('%s_%s' % (self.first_name, self.last_name))
                if Person.objects.filter(slug=s).exists():
                    self.slug = slugify('%s_%s_%s' % (self.id, self.first_name, self.last_name))
                else:
                    self.slug = s
        super(Person, self).save(*args, **kwargs)


    def to_json(self):
        return {'first_name': self.first_name, 'last_name': self.last_name}


    def __str__(self):
        return ('%s %s' % (self.first_name, self.last_name if self.last_name else '')).strip()


    class Meta:
        ordering = ('last_name', 'first_name')
        unique_together = ('last_name', 'first_name')
