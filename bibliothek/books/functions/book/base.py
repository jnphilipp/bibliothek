# -*- coding: utf-8 -*-

from books.models import Book
from django.utils.translation import ugettext as _
from links.models import Link
from persons.models import Person
from series.models import Series
from utils import lookahead, stdout


def create(title, authors=[], series_id=None, volume=0, links=[]):
    positions = [.33, 1.]

    book, created = Book.objects.get_or_create(title=title)
    if created:
        stdout.p([_('Id'), book.id], positions=positions)
        stdout.p([_('Title'), book.title], positions=positions)

        if len(authors) > 0:
            for (i, author_id), has_next in lookahead(enumerate(authors)):
                try:
                    author = Journal.objects.get(pk=author_id)
                    book.author.add(author)
                    stdout.p([_('Authors') if i == 0 else '', '%s: %s' % (author.id, str(author))], after=None if has_next else '_', positions=positions)
                except Journal.DoesNotExist:
                    stdout.p([_('Authors') if i == 0 else '', 'Person with id "%s" does not exist.' % author_id], positions=positions)
        else:
            stdout.p(['Authors', ''], positions=positions)

        for (i, url), has_next in lookahead(enumerate(links)):
            link, c = Link.objects.get_or_create(link=url)
            book.links.add(link)
            stdout.p([_('Links') if i == 0 else '', link.link], after=None if has_next else '_', positions=positions)

        book.save()
        stdout.p([_('Successfully added book "%(title)s" with id "%(id)s".') % {'title':book.title, 'id':book.id}], after='=', positions=[1.])
    else:
        stdout.p([_('The book "%(title)s" already exists with id "%(id)s", aborting...') % {'title':book.title, 'id':book.id}], after='=', positions=[1.])
    return book, created


def edit(book, field, value):
    assert field in ['title']

    if field == 'title':
        book.title = value
    book.save()
    stdout.p([_('Successfully edited book "%(title)s" with id "%(id)s".') % {'title':book.title, 'id':book.id}], positions=[1.])


def info(book):
    positions=[.33, 1.]
    stdout.p([_('Field'), _('Value')], positions=positions, after='=')
    stdout.p([_('Id'), book.id], positions=positions)
    stdout.p([_('Title'), book.title], positions=positions)

    if book.authors.count() > 0:
        for (i, author), has_next in lookahead(enumerate(book.authors.all())):
            if i == 0:
                stdout.p([_('Authors'), '%s: %s' % (author.id, str(author))], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (author.id, str(author))], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Authors'), ''], positions=positions)

    stdout.p([_('Series'), '%s: %s' % (book.series.id, book.series.name)], positions=positions)
    stdout.p([_('Volume'), book.volume], positions=positions)

    if book.links.count() > 0:
        for (i, link), has_next in lookahead(enumerate(book.links.all())):
            if i == 0:
                stdout.p([_('Links'), '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', '%s: %s' % (link.id, link.link)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p([_('Links'), ''], positions=positions)
