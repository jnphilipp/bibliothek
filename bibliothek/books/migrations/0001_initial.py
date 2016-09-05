# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-18 20:57
from __future__ import unicode_literals

import books.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('persons', '0001_initial'),
        ('series', '0001_initial'),
        ('links', '0001_initial'),
        ('genres', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(max_length=2048, unique=True)),
                ('title', books.models.TextFieldSingleLine(unique=True)),
                ('volume', models.FloatField(blank=True, default=0)),
                ('authors', models.ManyToManyField(blank=True, related_name='books', to='persons.Person')),
                ('links', models.ManyToManyField(blank=True, related_name='books', to='links.Link')),
                ('genres', models.ManyToManyField(blank=True, related_name='books', to='genres.Genre')),
                ('series', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='books', to='series.Series')),
            ],
            options={
                'verbose_name_plural': 'Books',
                'verbose_name': 'Book',
                'ordering': ('authors__last_name', 'authors__first_name', 'series', 'volume', 'title'),
            },
        ),
    ]
