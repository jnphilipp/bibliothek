# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ShelvesConfig(AppConfig):
    name = 'shelves'
    verbose_name = _('Shelf')
    verbose_name_plural = _('Shelves')
