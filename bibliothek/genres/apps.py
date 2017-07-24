# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class GenresConfig(AppConfig):
    name = 'genres'
    verbose_name = _('Genre')
    verbose_name_plural = _('Genres')
