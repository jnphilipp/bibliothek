# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2016-2022 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Bibliotheek Django app utils."""

from typing import Any, Generator, Iterable, Optional, Tuple


def lookahead(iterable: Optional[Iterable]) -> Generator[Tuple[Any, bool], None, None]:
    """Append to each element wheteher it is the last in the iterable."""
    if iterable is None:
        return None
    try:
        it = iter(iterable)
        last = next(it)
        for val in it:
            yield last, True
            last = val
        yield last, False
    except StopIteration:
        return None
