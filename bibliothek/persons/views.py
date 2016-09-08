# -*- coding: utf-8 -*-

from django.db.models import Count
from django.views import generic
from persons.models import Person


class ListView(generic.ListView):
    model = Person


    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['o'] = self.request.GET.get('o') if self.request.GET.get('o') else 'name'
        return context


    def get_queryset(self):
        o = self.request.GET.get('o') if self.request.GET.get('o') else 'name'
        persons = Person.objects.annotate(cb=Count('books'), cp=Count('papers'))
        if o.endswith('name'):
            persons = persons.order_by('last_name', 'first_name')
        else:
            persons = persons.order_by(o)
        return persons


class DetailView(generic.DetailView):
    model = Person


    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['o'] = self.request.GET.get('o') if self.request.GET.get('o') else 'title'
        context['books'] = self.object.books.annotate(ce=Count('editions')).order_by(context['o'])
        context['papers'] = self.object.papers.order_by(context['o'])
        return context
