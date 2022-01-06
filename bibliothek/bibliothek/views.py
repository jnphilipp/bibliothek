# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
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
"""Bibliothek Django app views."""

from books.models import Edition
from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, TextField, When
from django.shortcuts import render
from magazines.models import Issue
from papers.models import Paper
from shelves.models import Read


def dashboard(request):
    """Dashboard view."""
    edition_reads = (
        Read.objects.filter(content_type=ContentType.objects.get_for_model(Edition))
        .filter(started__isnull=False)
        .filter(finished__isnull=True)
        .annotate(
            title=Case(
                When(
                    editions__alternate_title__isnull=False,
                    then="editions__alternate_title",
                ),
                default="editions__book__title",
                output_field=TextField(),
            )
        )
        .order_by("started")
    )

    issue_reads = (
        Read.objects.filter(content_type=ContentType.objects.get_for_model(Issue))
        .filter(started__isnull=False)
        .filter(finished__isnull=True)
        .order_by("started")
    )

    paper_reads = (
        Read.objects.filter(content_type=ContentType.objects.get_for_model(Paper))
        .filter(started__isnull=False)
        .filter(finished__isnull=True)
        .order_by("started")
    )

    return render(request, "bibliothek/dashboard.html", locals())
