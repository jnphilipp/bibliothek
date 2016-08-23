# -*- coding: utf-8 -*-

from books.models import Book
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext as _
from links.models import Link
from persons.models import Person
from series.models import Series
from utils import lookahead, stdout


def create(title, authors=[], series=None, volume=0, links=[]):
    positions = [.33, 1.]

    book, created = Book.objects.get_or_create(title=title)
    if created:
        stdout.p([_('Id'), book.id], positions=positions)
        stdout.p([_('Title'), book.title], positions=positions)

        if len(authors) > 0:
            for (i, a), has_next in lookahead(enumerate(authors)):
                author, c = Person.objects.annotate(name=Concat('first_name', Value(' '), 'last_name')).filter(Q(pk=a if a.isdigit() else None) | Q(name__icontains=a)).get_or_create(defaults={'first_name':a[:a.rfind(' ')], 'last_name':a[a.rfind(' ') + 1 :]})
                book.authors.add(author)
                stdout.p([_('Authors') if i == 0 else '', '%s: %s' % (author.id, str(author))], after=None if has_next else '_', positions=positions)
        else:
            stdout.p([_('Authors'), ''], positions=positions)

        if series:
            book.series, c = Series.objects.filter(Q(pk=series if series.isdigit() else None) | Q(name__icontains=series)).get_or_create(defaults={'name':series})
            stdout.p([_('Series'), '%s: %s' % (book.series.id, book.series.name)], positions=positions)
        else:
            stdout.p([_('Series'), ''], positions=positions)

        if volume:
            book.volume = volume
            stdout.p([_('Volume'), book.volume], positions=positions)
        else:
            stdout.p([_('Volume'), ''], positions=positions)


        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.filter(Q(pk=url if url.isdigit() else None) | Q(link=url)).get_or_create(defaults={'link':url})
            book.links.add(link)
            stdout.p([_('Links') if i == 0 else '', '%s: %s' % (link.id, link.link)], after=None if has_next else '_', positions=positions)

        book.save()
        stdout.p([_('Successfully added book "%(title)s" with id "%(id)s".') % {'title':book.title, 'id':book.id}], after='=', positions=[1.])
    else:
        stdout.p([_('The book "%(title)s" already exists with id "%(id)s", aborting...') % {'title':book.title, 'id':book.id}], after='=', positions=[1.])
    return book, created


def edit(book, field, value):
    assert field in ['title', 'series', 'volume']

    if field == 'title':
        book.title = value
    elif field == 'series':
        book.series, created = Series.objects.filter(Q(pk=value if value.isdigit() else None) | Q(name__icontains=value)).get_or_create(defaults={'name':value})
    elif field == 'volume':
        book.volume = value
    book.save()
    stdout.p([_('Successfully edited book "%(title)s" with id "%(id)s".') % {'title':book.title, 'id':book.id}], positions=[1.])


def info(book):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), book.id], positions=positions)
    stdout.p([_('Title'), book.title], positions=positions)

    if book.authors.count() > 0:
        for (i, author), has_next in lookahead(enumerate(book.authors.all())):
            stdout.p([_('Authors') if i == 0 else '', '%s: %s' % (author.id, str(author))], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Authors'), ''], positions=positions)

    stdout.p([_('Series'), '%s: %s' % (book.series.id, book.series.name) if book.series else ''], positions=positions)
    stdout.p([_('Volume'), book.volume if book.volume else ''], positions=positions)

    if book.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(book.links.all())):
            stdout.p([_('Links') if i == 0 else '', '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)
