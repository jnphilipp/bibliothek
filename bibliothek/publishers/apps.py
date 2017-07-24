# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PublishersConfig(AppConfig):
    name = 'publishers'
    verbose_name = _('Publisher')
    verbose_name_plural = _('Publishers')
