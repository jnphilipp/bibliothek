# -*- coding: utf-8 -*-

from magazines.models import Issue
from utils import lookahead, stdout


def all(magazine):
    issues = Issue.objects.filter(magazine=magazine).order_by('published_on')
    _list([[issue.id, issue.issue, issue.published_on] for issue in issues], ['Id', 'Issue', 'Published on'], positions=[.05, .55, 1.])


def by_shelf(magazine, shelf):
    issues = Issue.objects.filter(magazine=magazine)
    if shelf == 'read':
        issues = issues.filter(issues__reads__isnull=False)
    elif shelf == 'unread':
        issues = issues.filter(issues__reads__isnull=True)
    _list([[issue.issue, issue.files.count()] for issue in issues], ['Name', '#Files'], positions=[.55, 1.])


def by_search(magazine, term=None):
    issues = Issue.objects.filter(magazine=magazine)
    if term:
        issues = issues.filter(issue__icontains=term)
    if stdout:
        _list([[issue.id, issue.issue, issue.files.count()] for issue in issues], ['Id', 'Name', '#Files'], positions=[.05, .55, 1.])
    return issues


def _list(issues, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for issue, has_next in lookahead(issues):
        stdout.p(issue, positions=positions, after='_' if has_next else '=')
