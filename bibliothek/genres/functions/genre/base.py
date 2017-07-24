# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from genres.models import Genre
from utils import lookahead, stdout


def create(name):
    positions = [.33, 1.]

    genre, created = Genre.objects.get_or_create(name=name)
    if created:
        stdout.p([_('Id'), genre.id], positions=positions)
        stdout.p([_('Name'), genre.name], positions=positions)
        genre.save()
        stdout.p([_('Successfully added genre "%(name)s" with id "%(id)s".') % {'name':genre.name, 'id':genre.id}], after='=', positions=[1.])
    else:
        stdout.p([_('The genre "%(name)s" already exists with id "%(id)s", aborting...') % {'name':genre.name, 'id':genre.id}], after='=', positions=[1.])
    return genre, created


def edit(genre, field, value):
    assert field in ['name']

    if field == 'name':
        genre.name = value
    genre.save()
    stdout.p([_('Successfully edited genre "%(name)s" with id "%(id)s".') % {'name':genre.name, 'id':genre.id}], positions=[1.])


def info(genre):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), genre.id], positions=positions)
    stdout.p([_('Name'), genre.name], positions=positions)

    if genre.books.count() > 0:
        for (i, book), has_next in lookahead(enumerate(genre.books.all())):
            if i == 0:
                stdout.p([_('Books'), '%s: %s %s' % (book.id, book.volume, book.title)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s %s' % (book.id, book.volume, book.title)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Books'), ''], positions=positions)
