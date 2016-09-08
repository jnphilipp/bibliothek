# -*- coding: utf-8 -*-

from django.db.models import Count
from django.views import generic
from books.models import Book


class ListView(generic.ListView):
    model = Book


    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['o'] = self.request.GET.get('o') if self.request.GET.get('o') else 'title'
        return context


    def get_queryset(self):
        o = self.request.GET.get('o') if self.request.GET.get('o') else 'title'
        return Book.objects.annotate(ce=Count('editions')).order_by(o)


class DetailView(generic.DetailView):
    model = Book
