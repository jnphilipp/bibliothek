# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Generated by Django 1.11.3 on 2017-07-24 10:52
# Copyright (C) 2016-2021 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
#
# This file is part of bibliothek.
#
# bibliothek is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# bibliothek is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with bibliothek.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


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
                ('title', models.TextField(unique=True, verbose_name='Title')),
                ('volume', models.FloatField(blank=True, default=0, verbose_name='Volume')),
                ('authors', models.ManyToManyField(blank=True, related_name='books', to='persons.Person', verbose_name='Authors')),
                ('genres', models.ManyToManyField(blank=True, related_name='books', to='genres.Genre', verbose_name='Genres')),
                ('links', models.ManyToManyField(blank=True, related_name='books', to='links.Link', verbose_name='Links')),
                ('series', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='books', to='series.Series', verbose_name='Series')),
            ],
            options={
                'verbose_name': 'Book',
                'verbose_name_plural': 'Books',
                'ordering': (django.db.models.expressions.Func(django.db.models.expressions.F('series__name'), function='LOWER'), 'volume', django.db.models.expressions.Func(django.db.models.expressions.F('title'), function='LOWER')),
            },
        ),
    ]
