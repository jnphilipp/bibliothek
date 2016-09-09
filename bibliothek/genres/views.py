# -*- coding: utf-8 -*-

from django.db.models import Count
from django.views import generic
from genres.models import Genre


class ListView(generic.ListView):
    model = Genre


    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['o'] = self.request.GET.get('o') if self.request.GET.get('o') else 'name'
        return context


    def get_queryset(self):
        o = self.request.GET.get('o') if self.request.GET.get('o') else 'name'
        return Genre.objects.annotate(cb=Count('books')).order_by(o)


class DetailView(generic.DetailView):
    model = Genre


    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['o'] = self.request.GET.get('o') if self.request.GET.get('o') else 'title'
        context['books'] = self.object.books.annotate(ce=Count('editions')).order_by(context['o'])
        return context
