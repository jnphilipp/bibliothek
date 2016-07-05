# -*- coding: utf-8 -*-

from django.db import models


class Link(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    link = models.URLField(max_length=4096, unique=True)


    def __str__(self):
        return self.link


    class Meta:
        ordering = ('link',)
        verbose_name = ' link'
