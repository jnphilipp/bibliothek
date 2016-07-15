# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render
from journals.models import Journal


def journals(request):
    journals = Journal.objects.all()
    return render(request, 'journals/journal/journals.html', locals())


def journal(request, slug):
    journal = get_object_or_404(Journal, slug=slug)
    return render(request, 'journals/journal/journal.html', locals())
