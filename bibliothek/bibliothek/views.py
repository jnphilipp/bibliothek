# -*- coding: utf-8 -*-

from books.models import Edition
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render
from magazines.models import Issue
from papers.models import Paper
from shelves.models import Read


def dashboard(request):
    edition_reads = Read.objects.filter(content_type=ContentType.objects.get_for_model(Edition)).filter(started__isnull=False).filter(finished__isnull=True).order_by('started')
    issue_reads = Read.objects.filter(content_type=ContentType.objects.get_for_model(Issue)).filter(started__isnull=False).filter(finished__isnull=True).order_by('started')
    paper_reads = Read.objects.filter(content_type=ContentType.objects.get_for_model(Paper)).filter(started__isnull=False).filter(finished__isnull=True).order_by('started')
    return render(request, 'bibliothek/dashboard.html', locals())
