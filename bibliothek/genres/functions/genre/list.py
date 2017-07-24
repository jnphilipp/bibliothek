# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from genres.models import Genre
from utils import lookahead, stdout


def all():
    genres = Genre.objects.all()
    _list([[genre.id, genre.name] for genre in genres], [_('Id'), _('Name')], positions=[.05, 1.])
    return genres


def by_term(term):
    genres = Genre.objects.filter(Q(pk=term if term.isdigit() else None) | Q(name__icontains=term))
    _list([[genre.id, genre.name] for genre in genres], [_('Id'), _('Name')], positions=[.05, 1.])
    return genres


def _list(genres, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for genres, has_next in lookahead(genres):
        stdout.p(genres, positions=positions, after='_' if has_next else '=')
