# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render
from papers.models import Paper


def papers(request):
    o = request.GET.get('o') if request.GET.get('o') else 'title'
    papers = Paper.objects.all().order_by(o)
    return render(request, 'papers/paper/papers.html', locals())


def paper(request, slug):
    paper = get_object_or_404(Paper, slug=slug)
    return render(request, 'papers/paper/paper.html', locals())
