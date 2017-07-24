# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LinksConfig(AppConfig):
    name = 'links'
    verbose_name = _('Link')
    verbose_name_plural = _('Links')
