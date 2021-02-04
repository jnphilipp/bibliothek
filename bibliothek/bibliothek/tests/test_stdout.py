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

from bibliothek import stdout
from django.test import TestCase
from io import StringIO


class StdoutTestCase(TestCase):
    def test_write(self):
        with StringIO() as cout:
            stdout.write([1, 2], positions=[0.3], line_length=20, file=cout)
            self.assertEquals(
                "1     2             \n____________________\n", cout.getvalue()
            )

        with StringIO() as cout:
            stdout.write([1, 2], positions=[0.5], line_length=20, file=cout)
            self.assertEquals(
                "1         2         \n____________________\n", cout.getvalue()
            )

        with StringIO() as cout:
            stdout.write([1, 2], positions=[0.8], line_length=20, file=cout)
            self.assertEquals(
                "1               2   \n____________________\n", cout.getvalue()
            )

        with StringIO() as cout:
            stdout.write(["1", "2"], None, [0.5], 20, cout)
            self.assertEquals("1         2         \n", cout.getvalue())

        with StringIO() as cout:
            stdout.write(["1", "2"], "#", [0.5], 20, cout)
            self.assertEquals(
                "1         2         \n####################\n", cout.getvalue()
            )

        with StringIO() as cout:
            stdout.write(["1", "2"], "#", [0.5], 10, cout)
            self.assertEquals("1    2    \n##########\n", cout.getvalue())
