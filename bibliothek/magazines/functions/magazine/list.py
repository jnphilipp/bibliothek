# -*- coding: utf-8 -*-

from magazines.models import Magazine
from utils import lookahead, stdout


def all():
    magazines = Magazine.objects.all()
    _list([[magazine.name, magazine.issues.count()] for magazine in magazines], ['Name', '#Issues'], positions=[.55, 1.])


def by_shelf(shelf):
    magazines = Magazine.objects.all()
    if shelf == 'read':
        magazines = magazines.filter(issues__reads__isnull=False)
    elif shelf == 'unread':
        magazines = magazines.filter(issues__reads__isnull=True)
    _list([[magazine.name, magazine.issues.count()] for magazine in magazines], ['Name', '#Issues'], positions=[.55, 1.])


def by_term(term):
    magazines = Magazine.objects.filter(name__icontains=term)
    _list([[magazine.name, magazine.issues.count()] for magazine in magazines], ['Name', '#Issues'], positions=[.55, 1.])
    return magazines


def _list(magazines, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for magazine, has_next in lookahead(magazines):
        stdout.p(magazine, positions=positions, after='_' if has_next else '=')
