# -*- coding: utf-8 -*-

from magazines.models import Issue
from utils import lookahead, stdout


def all(magazine):
    issues = Issue.objects.filter(magazine=magazine).order_by('published_on')
    _list([[issue.issue, issue.published_on, issue.files.count()] for issue in issues], ['Issue', 'Published on', '#Files'], positions=[.45, .60, 1.])
    return issues


def by_shelf(magazine, shelf):
    issues = Issue.objects.filter(magazine=magazine)
    if shelf == 'read':
        issues = issues.filter(issues__reads__isnull=False)
    elif shelf == 'unread':
        issues = issues.filter(issues__reads__isnull=True)
    magazines = magazines.distinct()
    _list([[issue.issue, issue.published_on, issue.files.count()] for issue in issues], ['Name', 'Published on', '#Files'], positions=[.45, .60, 1.])
    return issues


def by_term(magazine, term):
    issues = Issue.objects.filter(magazine=magazine).filter(issue__icontains=term)
    _list([[issue.issue, issue.published_on, issue.files.count()] for issue in issues], ['Name', 'Published on', '#Files'], positions=[.45, .60, 1.])
    return issues


def _list(issues, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for issue, has_next in lookahead(issues):
        stdout.p(issue, positions=positions, after='_' if has_next else '=')
