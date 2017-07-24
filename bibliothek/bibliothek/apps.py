# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BibliothekConfig(AppConfig):
    name = 'bibliothek'
    verbose_name = _('Library')
    verbose_name_plural = _('Libraries')
