# -*- coding: utf-8 -*-

from utils import stdout

from . import list as book_list


def by_term(term):
    books = book_list.by_term(term)

    if books.count() == 0:
        stdout.p(['No book found.'], after='=', positions=[1.])
        return None
    elif books.count() > 1:
        stdout.p(['More than one book found.'], after='=', positions=[1.])
        return None
    print('\n')
    return books[0]
