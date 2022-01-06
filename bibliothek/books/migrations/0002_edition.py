# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Generated by Django 1.11.3 on 2017-07-24 10:52
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
import django.db.models.expressions
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('languages', '0001_initial'),
        ('bindings', '0001_initial'),
        ('publishers', '0001_initial'),
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Edition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('alternate_title', models.TextField(blank=True, null=True, verbose_name='Alternate title')),
                ('isbn', models.CharField(blank=True, max_length=13, null=True, verbose_name='ISBN')),
                ('publishing_date', models.DateField(blank=True, null=True, verbose_name='Publishing date')),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='files', verbose_name='Cover image')),
                ('bibtex', models.TextField(blank=True, null=True, verbose_name='BibTex')),
                ('binding', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='editions', to='bindings.Binding', verbose_name='Binding')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='editions', to='books.Book', verbose_name='Book')),
                ('languages', models.ManyToManyField(blank=True, related_name='editions', to='languages.Language', verbose_name='Languages')),
                ('publisher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='editions', to='publishers.Publisher', verbose_name='Publisher')),
            ],
            options={
                'ordering': (django.db.models.expressions.Func(django.db.models.expressions.F('book__series__name'), function='LOWER'), 'book__volume', django.db.models.expressions.Func(django.db.models.expressions.F('book__title'), function='LOWER'), 'publishing_date'),
                'verbose_name': 'Edition',
                'verbose_name_plural': 'Editions',
            },
        ),
    ]
