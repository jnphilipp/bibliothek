# -*- coding: utf-8 -*-

from bindings.models import Binding
from django.utils.translation import ugettext as _
from utils import lookahead, stdout


def create(name):
    positions = [.33, 1.]

    binding, created = Binding.objects.get_or_create(name=name)
    if created:
        stdout.p([_('Id'), binding.id], positions=positions)
        stdout.p([_('Name'), binding.name], positions=positions)
        binding.save()
        stdout.p([_('Successfully added binding "%(name)s" with id "%(id)s".') % {'name':binding.name, 'id':binding.id}], after='=', positions=[1.])
    else:
        stdout.p([_('The binding "%(name)s" already exists with id "%(id)s", aborting...') % {'name':binding.name, 'id':binding.id}], after='=', positions=[1.])
    return binding, created


def edit(binding, field, value):
    assert field in ['name']

    if field == 'name':
        binding.name = value
    binding.save()
    stdout.p([_('Successfully edited binding "%(name)s" with id "%(id)s".') % {'name':binding.name, 'id':binding.id}], positions=[1.])


def info(binding):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), binding.id], positions=positions)
    stdout.p([_('Name'), binding.name], positions=positions)
