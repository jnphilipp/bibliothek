# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class MagazinesConfig(AppConfig):
    name = 'magazines'
    verbose_name = _('Magazine')
    verbose_name_plural = _('Magazines')
