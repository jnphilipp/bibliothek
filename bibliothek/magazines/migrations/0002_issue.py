# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-23 19:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import magazines.models


class Migration(migrations.Migration):

    dependencies = [
        ('languages', '0001_initial'),
        ('links', '0001_initial'),
        ('magazines', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(max_length=2048)),
                ('issue', magazines.models.TextFieldSingleLine()),
                ('published_on', models.DateField(blank=True, null=True)),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='issues')),
                ('languages', models.ManyToManyField(blank=True, related_name='issues', to='languages.Language')),
                ('links', models.ManyToManyField(blank=True, related_name='issues', to='links.Link')),
                ('magazine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issues', to='magazines.Magazine')),
            ],
            options={
                'ordering': ('magazine', 'issue'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='issue',
            unique_together=set([('magazine', 'issue')]),
        ),
    ]
