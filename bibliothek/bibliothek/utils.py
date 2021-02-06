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

from typing import Any, Generator, Iterable, Tuple


def lookahead(iterable: Iterable) -> Generator[Tuple[Any, bool], None, None]:
    """Append to each element wheteher it is the last in the iterable."""
    try:
        it = iter(iterable)
        last = next(it)
        for val in it:
            yield last, True
            last = val
        yield last, False
    except StopIteration:
        return None
