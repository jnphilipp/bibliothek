# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BindingsConfig(AppConfig):
    name = 'bindings'
    verbose_name = _('Binding')
    verbose_name_plural = _('Bindings')
