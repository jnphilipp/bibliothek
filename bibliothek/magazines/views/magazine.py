# -*- coding: utf-8 -*-

from django.db.models import Count
from django.views import generic
from magazines.models import Magazine


class ListView(generic.ListView):
    model = Magazine


    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['o'] = self.request.GET.get('o') if self.request.GET.get('o') else 'name'
        return context


    def get_queryset(self):
        o = self.request.GET.get('o') if self.request.GET.get('o') else 'name'
        return Magazine.objects.annotate(ci=Count('issues')).order_by(o)


class DetailView(generic.DetailView):
    model = Magazine


    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['o'] = self.request.GET.get('o') if self.request.GET.get('o') else '-published_on'
        context['issues'] = self.object.issues.order_by(context['o'])
        return context
