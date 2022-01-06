# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
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

import os

from files.models import File
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, TestCase
from tempfile import mkdtemp, NamedTemporaryFile


class FileModelTestCase(TestCase):
    @override_settings(MEDIA_ROOT=mkdtemp())
    def test_from_to_dict(self):
        file, created = File.objects.get_or_create(
            file=SimpleUploadedFile("test.txt", b"Lorem ipsum dolorem")
        )
        self.assertTrue(created)
        self.assertIsNotNone(file.id)
        self.assertEquals(
            {"path": os.path.join(settings.MEDIA_ROOT, "files/test.txt")},
            file.to_dict(),
        )

        with NamedTemporaryFile() as f:
            f.write(b"Lorem ipsum dolorem")
            file, created = File.from_dict({"path": f.name})
            self.assertTrue(created)
            self.assertIsNotNone(file.id)
            self.assertEquals(
                os.path.basename(f.name), os.path.basename(file.file.name)
            )
            self.assertEquals(f"files/{os.path.basename(f.name)}", file.file.name)
            self.assertEquals(
                {
                    "path": os.path.join(
                        settings.MEDIA_ROOT, "files", os.path.basename(f.name)
                    )
                },
                file.to_dict(),
            )
            self.assertEquals((file, False), File.from_dict(file.to_dict()))

    @override_settings(MEDIA_ROOT=mkdtemp())
    def test_save(self):
        file = File(file=SimpleUploadedFile("test.txt", b"Lorem ipsum dolorem"))
        file.save()
        self.assertIsNotNone(file.id)
        self.assertEquals("files/test.txt", file.file.name)
