# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from series.models import Series
from utils import lookahead, stdout


def create(name):
    positions = [.33, 1.]

    series, created = Series.objects.get_or_create(name=name)
    if created:
        stdout.p([_('Id'), series.id], positions=positions)
        stdout.p([_('Name'), series.name], positions=positions)
        series.save()
        stdout.p([_('Successfully added series "%(name)s" with id "%(id)s".') % {'name':series.name, 'id':series.id}], after='=', positions=[1.])
    else:
        stdout.p([_('The series "%(name)s" already exists with id "%(id)s", aborting...') % {'name':series.name, 'id':series.id}], after='=', positions=[1.])
    return series, created


def edit(series, field, value):
    assert field in ['name']

    if field == 'name':
        series.name = value
    series.save()
    stdout.p([_('Successfully edited series "%(name)s" with id "%(id)s".') % {'name':series.name, 'id':series.id}], positions=[1.])


def info(series):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), series.id], positions=positions)
    stdout.p([_('Name'), series.name], positions=positions)

    if series.books.count() > 0:
        for (i, book), has_next in lookahead(enumerate(series.books.all().order_by('volume'))):
            if i == 0:
                stdout.p([_('Books'), '%s: %s %s' % (book.id, book.volume, book.title)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s %s' % (book.id, book.volume, book.title)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Books'), ''], positions=positions)
