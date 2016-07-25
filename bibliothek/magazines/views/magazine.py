# -*- coding: utf-8 -*-

from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from magazines.models import Magazine


def magazines(request):
    o = request.GET.get('o') if request.GET.get('o') else 'name'
    magazines = Magazine.objects.annotate(ci=Count('issues')).all().order_by(o)
    return render(request, 'magazines/magazine/magazines.html', locals())


def magazine(request, slug):
    o = request.GET.get('o') if request.GET.get('o') else '-published_on'
    magazine = get_object_or_404(Magazine, slug=slug)
    issues = magazine.issues.all().order_by(o)
    return render(request, 'magazines/magazine/magazine.html', locals())
