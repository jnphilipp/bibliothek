# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Generated by Django 2.1.1 on 2018-09-20 15:10
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

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0001_initial'),
        ('books', '0003_edition_links'),
    ]

    operations = [
        migrations.AddField(
            model_name='edition',
            name='persons',
            field=models.ManyToManyField(blank=True, related_name='editions', to='persons.Person', verbose_name='Persons'),
        ),
    ]
