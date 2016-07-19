# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render
from persons.models import Person


def persons(request):
    persons = Person.objects.all()
    return render(request, 'persons/person/persons.html', locals())


def person(request, slug):
    person = get_object_or_404(Person, slug=slug)
    return render(request, 'persons/person/person.html', locals())
