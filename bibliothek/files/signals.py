# -*- coding: utf-8 -*-
# Copyright (C) 2016-2021 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
#
# This file is part of bibliothek.
#
# bibliothek is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# bibliothek is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with bibliothek.  If not, see <http://www.gnu.org/licenses/>.
"""Files app signals."""

import os

from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from files.models import File


@receiver(pre_delete, sender=File)
def delete_files(sender, instance, **kwargs):
    """Delete file when deleting file from DB."""
    os.remove(os.path.join(settings.MEDIA_ROOT, instance.file.name))
