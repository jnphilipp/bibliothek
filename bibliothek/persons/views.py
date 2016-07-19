# -*- coding: utf-8 -*-

from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from persons.models import Person


def persons(request):
    o = request.GET.get('o') if request.GET.get('o') else 'name'
    persons = Person.objects.annotate(cp=Count('papers')).all()
    if o.endswith('name'):
        persons = persons.order_by('last_name', 'first_name')
    else:
        persons = persons.order_by(o)
    return render(request, 'persons/person/persons.html', locals())


def person(request, slug):
    o = request.GET.get('o') if request.GET.get('o') else 'title'
    person = get_object_or_404(Person, slug=slug)
    papers = person.papers.all().order_by(o)
    return render(request, 'persons/person/person.html', locals())
