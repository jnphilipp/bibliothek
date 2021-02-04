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

from bibliothek.utils import lookahead
from django.test import TestCase


class UtilsTestCase(TestCase):
    def test_lookahead(self):
        self.assertEquals(
            [(1, True), (2, True), (3, False)], list(lookahead([1, 2, 3]))
        )

        self.assertEquals(
            [("1", True), ("2", True), ("3", False)], list(lookahead(["1", "2", "3"]))
        )
