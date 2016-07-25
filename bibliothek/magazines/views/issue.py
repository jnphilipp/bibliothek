# -*- coding: utf-8 -*-

from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from magazines.models import Issue, Magazine


def issues(request, magazine_slug):
    o = request.GET.get('o') if request.GET.get('o') else 'issue'
    magazine = get_object_or_404(Magazine, slug=magazine_slug)
    issues = Issue.objects.filter(magazine=magazine).order_by(o)
    return render(request, 'magazines/issue/issues.html', locals())


def issue(request, magazine_slug, issue_slug):
    magazine = get_object_or_404(Magazine, slug=magazine_slug)
    issue = get_object_or_404(Issue, slug=issue_slug)
    return render(request, 'magazines/issue/issue.html', locals())
