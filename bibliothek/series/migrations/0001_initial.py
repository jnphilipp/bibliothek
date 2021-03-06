# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-24 09:58
from __future__ import unicode_literals

import bibliothek.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('links', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('slug', models.SlugField(max_length=2048, unique=True, verbose_name='Slug')),
                ('name', bibliothek.fields.SingleLineTextField(unique=True, verbose_name='Name')),
                ('links', models.ManyToManyField(blank=True, related_name='series', to='links.Link', verbose_name='Links')),
            ],
            options={
                'verbose_name_plural': 'Series',
                'ordering': ('name',),
                'verbose_name': 'Series',
            },
        ),
    ]
