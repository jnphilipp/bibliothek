# -*- coding: utf-8 -*-

from django.apps import AppConfig


class FilesConfig(AppConfig):
    name = 'files'
    verbose_name = 'File'
    verbose_name_plural = 'Files'


    def ready(self):
        import files.signals
