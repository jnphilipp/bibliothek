# -*- coding: utf-8 -*-

from django.db.models import Count
from django.views import generic
from journals.models import Journal


class ListView(generic.ListView):
    model = Journal


    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['o'] = self.request.GET.get('o') if self.request.GET.get('o') else 'name'
        return context


    def get_queryset(self):
        o = self.request.GET.get('o') if self.request.GET.get('o') else 'name'
        return Journal.objects.annotate(cp=Count('papers')).order_by(o)


class DetailView(generic.DetailView):
    model = Journal


    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['o'] = self.request.GET.get('o') if self.request.GET.get('o') else 'title'
        context['papers'] = self.object.papers.order_by(context['o'])
        return context
