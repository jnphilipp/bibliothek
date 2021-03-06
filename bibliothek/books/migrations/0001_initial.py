# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-24 10:52
from __future__ import unicode_literals

import bibliothek.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('links', '0001_initial'),
        ('genres', '0001_initial'),
        ('persons', '0001_initial'),
        ('series', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('slug', models.SlugField(max_length=2048, unique=True, verbose_name='Slug')),
                ('title', bibliothek.fields.SingleLineTextField(unique=True, verbose_name='Title')),
                ('volume', models.FloatField(blank=True, default=0, verbose_name='Volume')),
                ('authors', models.ManyToManyField(blank=True, related_name='books', to='persons.Person', verbose_name='Authors')),
                ('genres', models.ManyToManyField(blank=True, related_name='books', to='genres.Genre', verbose_name='Genres')),
                ('links', models.ManyToManyField(blank=True, related_name='books', to='links.Link', verbose_name='Links')),
                ('series', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='books', to='series.Series', verbose_name='Series')),
            ],
            options={
                'verbose_name': 'Book',
                'verbose_name_plural': 'Books',
                'ordering': ('series', 'volume', 'title'),
            },
        ),
    ]
