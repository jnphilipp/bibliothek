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
# Generated by Django 4.0.1 on 2022-01-31 13:07

import re

from bibtexparser.bparser import BibTexParser
from django.db import migrations, models


def default_dois(apps, schema_editor):
    Paper = apps.get_model("papers", "Paper")

    for paper in Paper.objects.all():
        if not paper.bibtex:
            continue

        bib_database = BibTexParser(common_strings=True, homogenize_fields=True).parse(
            paper.bibtex
        )
        if "doi" in bib_database.entries[0]:
            if bib_database.entries[0]["doi"].startswith("doi:"):
                paper.doi = bib_database.entries[0]["doi"][4:]
            elif bib_database.entries[0]["doi"].startswith("http"):
                paper.doi = re.sub(
                    r"https?://[^/]+/", "", bib_database.entries[0]["doi"]
                )
            else:
                paper.doi = bib_database.entries[0]["doi"]
            paper.save()


class Migration(migrations.Migration):

    dependencies = [
        ("papers", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="paper",
            name="doi",
            field=models.TextField(
                blank=True, null=True, unique=True, verbose_name="DOI"
            ),
        ),
        migrations.RunPython(default_dois),
    ]
