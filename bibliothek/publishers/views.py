# -*- coding: utf-8 -*-

from django.db.models import Count
from django.views import generic
from publishers.models import Publisher


class ListView(generic.ListView):
    model = Publisher


    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['o'] = self.request.GET.get('o') if self.request.GET.get('o') else 'name'
        return context


    def get_queryset(self):
        o = self.request.GET.get('o') if self.request.GET.get('o') else 'name'
        publishers = Publisher.objects.annotate(ce=Count('editions')).order_by(o)
        return publishers


class DetailView(generic.DetailView):
    model = Publisher


    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['o'] = self.request.GET.get('o') if self.request.GET.get('o') else 'book__title'
        context['editions'] = self.object.editions.order_by(context['o'])
        return context
