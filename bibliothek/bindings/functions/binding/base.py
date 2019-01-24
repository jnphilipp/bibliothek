# -*- coding: utf-8 -*-
# Copyright (C) 2017-2019 Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>
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

from bindings.models import Binding
from django.utils.translation import ugettext_lazy as _
from utils import lookahead, stdout


def create(name):
    positions = [.33, 1.]

    binding, created = Binding.objects.get_or_create(name=name)
    if created:
        stdout.p([_('Id'), binding.id], positions=positions)
        stdout.p([_('Name'), binding.name], positions=positions)
        binding.save()
        msg = _('Successfully added binding "%(name)s" with id "%(id)s".')
        stdout.p([msg % {'name': binding.name, 'id': binding.id}], after='=',
                 positions=[1.])
    else:
        msg = _('The binding "%(name)s" already exists with id "%(id)s", ' +
                'aborting...')
        stdout.p([msg % {'name': binding.name, 'id': binding.id}], after='=',
                 positions=[1.])
    return binding, created


def edit(binding, field, value):
    assert field in ['name']

    if field == 'name':
        binding.name = value
    binding.save()
    msg = _('Successfully edited binding "%(name)s" with id "%(id)s".')
    stdout.p([msg % {'name':binding.name, 'id':binding.id}], positions=[1.])


def info(binding):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), binding.id], positions=positions)
    stdout.p([_('Name'), binding.name], positions=positions)
