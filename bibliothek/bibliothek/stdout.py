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
"""Bibliothek Django app stdout."""

import sys

from typing import List, Optional, Sequence, TextIO, Union


def write(
    fields: Union[Sequence, str],
    after: Optional[str] = "_",
    positions: List[float] = [],
    line_length: int = 100,
    file: TextIO = sys.stdout,
):
    """Write fields formatted as table to file.

    Args:
        * fields: fields to print
        * after: if not empty symbol to write after as last line
        * positions: list of column positions
        * line_length: line length
        * file: file to write to, default sys.stdout
    """
    assert after is None or len(after) == 0 or len(after) == 1
    assert len(positions) == 0 or [pos > 1.0 for pos in positions]
    assert line_length > 0

    if len(positions) == 0 or positions[-1] <= 1.0:
        positions += [1.0]

    if isinstance(fields, str) or not isinstance(fields, list):
        fields = [fields]

    def _write(fields: Sequence, positions: List[int]):
        line = ""
        rfields = []
        for i in range(len(fields)):
            line += str(fields[i]) if fields[i] else ""

            if len(line) > positions[i]:
                rf = line.rfind(" ", positions[i - 1] if i > 0 else 0, positions[i])
                if rf > 0:
                    rfields.append(line[rf + 1 :])
                    line = line[:rf]
                else:
                    line = line[: positions[i]]
                    rfields.append(line[positions[i] :])
            else:
                rfields.append("")
            line += " " * (positions[i] - len(line))
        file.write(f"{line}\n")
        if max([f != "" for f in rfields]):
            _write(rfields, positions)

    _write(fields, [int(line_length * pos) for pos in positions])
    if after:
        file.write(f"{after * line_length}\n")
