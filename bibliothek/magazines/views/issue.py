# -*- coding: utf-8 -*-

from django.views import generic
from magazines.models import Issue


class DetailView(generic.DetailView):
    model = Issue
    slug_field = 'magazine__slug'
