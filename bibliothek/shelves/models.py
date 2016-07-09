# -*- coding: utf-8 -*-

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Acquisition(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    date = models.DateField(blank=True, null=True)
    price = models.FloatField(default=0)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


    def __str__(self):
        return 'acquisition "%s"' % self.content_object


    class Meta:
        ordering = ('date',)
        verbose_name = ' acquisition'


class Read(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    started = models.DateField(verbose_name=' date started', blank=True, null=True)
    finished = models.DateField(verbose_name=' date finished', blank=True, null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


    def __str__(self):
        return 'read "%s"' % self.content_object


    class Meta:
        ordering = ('started', 'finished')
        verbose_name = ' read'
