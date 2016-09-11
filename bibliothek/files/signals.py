# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from files.models import File


@receiver(pre_delete, sender=File)
def delete_old_resumption_tokens(sender, instance, **kwargs):
    print(os.path.join(settings.MEDIA_ROOT, instance.file.name))
    os.remove(os.path.join(settings.MEDIA_ROOT, instance.file.name))
