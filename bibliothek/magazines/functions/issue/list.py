# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from magazines.models import Issue
from utils import lookahead, stdout


def all(magazine):
    issues = Issue.objects.filter(magazine=magazine).order_by('published_on')
    _list([[issue.id, issue.issue, issue.published_on, issue.files.count()] for issue in issues], [_('Id'), _('Issue'), _('Published on'), _('#Files')], positions=[.05, .45, .60, 1.])
    return issues


def by_shelf(magazine, shelf):
    issues = Issue.objects.filter(magazine=magazine)
    if shelf == 'read':
        issues = issues.filter(issues__reads__isnull=False)
    elif shelf == 'unread':
        issues = issues.filter(issues__reads__isnull=True)
    magazines = magazines.distinct()
    _list([[issue.id, issue.issue, issue.published_on, issue.files.count()] for issue in issues], [_('Id'), _('Issue'), _('Published on'), _('#Files')], positions=[.05, .45, .60, 1.])
    return issues


def by_term(magazine, term):
    issues = Issue.objects.filter(Q(magazine=magazine) & (Q(pk=term if term.isdigit() else None) | Q(issue__icontains=term)))
    _list([[issue.id, issue.issue, issue.published_on, issue.files.count()] for issue in issues], [_('Id'), _('Issue'), _('Published on'), _('#Files')], positions=[.05, .45, .60, 1.])
    return issues


def _list(issues, fields, positions):
    stdout.p(fields, positions=positions, after='=')
    for issue, has_next in lookahead(issues):
        stdout.p(issue, positions=positions, after='_' if has_next else '=')
