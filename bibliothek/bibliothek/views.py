# -*- coding: utf-8 -*-

from books.models import Book
from django.shortcuts import get_object_or_404, render
from magazines.models import Issue
from papers.models import Paper


def dashboard(request):
    bo = request.GET.get('bo') if request.GET.get('bo') else 'title'
    books = Book.objects.filter(editions__reads__started__isnull=False).filter(editions__reads__finished__isnull=True).order_by(bo)

    mo = request.GET.get('mo') if request.GET.get('mo') else 'magazine'
    issues = Issue.objects.filter(reads__started__isnull=False).filter(reads__finished__isnull=True).order_by(mo)

    po = request.GET.get('po') if request.GET.get('po') else 'title'
    papers = Paper.objects.filter(reads__started__isnull=False).filter(reads__finished__isnull=True).order_by(po)

    return render(request, 'bibliothek/dashboard.html', locals())
