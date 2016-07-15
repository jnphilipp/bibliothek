# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render
from papers.models import Paper


def papers(request):
    papers = Paper.objects.all()
    return render(request, 'papers/paper/papers.html', locals())


def paper(request, slug):
    paper = get_object_or_404(Paper, slug=slug)
    return render(request, 'papers/paper/paper.html', locals())
