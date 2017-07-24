# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PapersConfig(AppConfig):
    name = 'papers'
    verbose_name = _('Paper')
    verbose_name_plural = _('Papers')
