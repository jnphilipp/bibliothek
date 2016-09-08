# -*- coding: utf-8 -*-

from django.views import generic
from books.models import Edition


class DetailView(generic.DetailView):
    model = Edition
    slug_field = 'book__slug'
