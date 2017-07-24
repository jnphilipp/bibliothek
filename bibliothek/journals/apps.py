# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class JournalsConfig(AppConfig):
    name = 'journals'
    verbose_name = _('Journal')
    verbose_name_plural = _('Journals')
