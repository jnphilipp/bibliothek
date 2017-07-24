# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SeriesConfig(AppConfig):
    name = 'series'
    verbose_name = _('Series')
    verbose_name_plural = _('Series')
