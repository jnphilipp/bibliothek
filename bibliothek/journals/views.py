# -*- coding: utf-8 -*-

from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from journals.models import Journal


def journals(request):
    o = request.GET.get('o') if request.GET.get('o') else 'name'
    journals = Journal.objects.annotate(cp=Count('papers')).all().order_by(o)
    return render(request, 'journals/journal/journals.html', locals())


def journal(request, slug):
    o = request.GET.get('o') if request.GET.get('o') else 'title'
    journal = get_object_or_404(Journal, slug=slug)
    papers = journal.papers.all().order_by(o)
    return render(request, 'journals/journal/journal.html', locals())
