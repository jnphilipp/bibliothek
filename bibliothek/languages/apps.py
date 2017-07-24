# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LanguagesConfig(AppConfig):
    name = 'languages'
    verbose_name = _('Language')
    verbose_name_plural = _('Languages')
