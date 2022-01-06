# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Generated by Django 1.11.3 on 2017-07-24 10:38
# Copyright (C) 2016-2022 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('persons', '0001_initial'),
        ('journals', '0001_initial'),
        ('links', '0001_initial'),
        ('languages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('slug', models.SlugField(max_length=2048, unique=True, verbose_name='Slug')),
                ('title', models.TextField(unique=True, verbose_name='Title')),
                ('volume', models.TextField(blank=True, null=True, verbose_name='Volume')),
                ('publishing_date', models.DateField(blank=True, null=True, verbose_name='Publishing date')),
                ('bibtex', models.TextField(blank=True, null=True, verbose_name='BibTex')),
                ('authors', models.ManyToManyField(blank=True, related_name='papers', to='persons.Person', verbose_name='Authors')),
                ('journal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='papers', to='journals.Journal', verbose_name='Journal')),
                ('languages', models.ManyToManyField(blank=True, related_name='papers', to='languages.Language', verbose_name='Languages')),
                ('links', models.ManyToManyField(blank=True, related_name='papers', to='links.Link', verbose_name='Links')),
            ],
            options={
                'ordering': (django.db.models.expressions.Func(django.db.models.expressions.F('journal__name'), function='LOWER'), django.db.models.expressions.Func(django.db.models.expressions.F('volume'), function='LOWER'), django.db.models.expressions.Func(django.db.models.expressions.F('title'), function='LOWER')),
                'verbose_name': 'Paper',
                'verbose_name_plural': 'Papers',
            },
        ),
        migrations.AlterUniqueTogether(
            name='paper',
            unique_together=set([('journal', 'volume', 'title')]),
        ),
    ]
