#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""bibliothek
Copyright (C) 2016 jnphilipp <me@jnphilipp.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import django
import os

from argparse import ArgumentParser, RawTextHelpFormatter
from bibliothek.bibliothek import settings, GConfig


def init():
    if not os.path.exists(settings.app_data_dir):
        os.makedirs(settings.app_data_dir)
        from django.core.management import execute_from_command_line
        execute_from_command_line(['', 'migrate'])


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bibliothek.bibliothek.settings")
    django.setup()
    gconf = GConfig(settings.app_identifier)
    gconf.load()
    init()


    parser = ArgumentParser(prog=settings.app_name, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version=settings.app_version)


    args = parser.parse_args()
    if args.sub:
        args.func(args)
    else:
        parser.print_usage()
