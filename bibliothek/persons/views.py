# -*- coding: utf-8 -*-

from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from persons.models import Person


def persons(request):
    o = request.GET.get('o') if request.GET.get('o') else 'name'
    persons = Person.objects.annotate(cb=Count('books'), cp=Count('papers')).all()
    if o.endswith('name'):
        persons = persons.order_by('last_name', 'first_name')
    else:
        persons = persons.order_by(o)
    return render(request, 'persons/person/persons.html', locals())


def person(request, slug):
    bo = request.GET.get('bo') if request.GET.get('bo') else 'title'
    po = request.GET.get('po') if request.GET.get('po') else 'title'
    person = get_object_or_404(Person, slug=slug)
    books = person.books.all().order_by(bo)
    papers = person.papers.all().order_by(po)
    return render(request, 'persons/person/person.html', locals())
