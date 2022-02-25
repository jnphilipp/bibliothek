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

from typing import Any, Dict, Generator, Iterable, Optional, Tuple


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


def concat(*args: Tuple[int, Dict[str, int]]) -> Tuple[int, Dict[str, int]]:
    """Concatenate."""
    n = 0
    d: Dict[str, int] = dict()
    for arg in args:
        n += arg[0]
        for k, v in arg[1].items():
            if k in d:
                d[k] += v
            else:
                d[k] = v
    return n, d
