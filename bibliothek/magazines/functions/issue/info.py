# -*- coding: utf-8 -*-

from utils import lookahead, stdout


def show(issue):
    positions=[.33, 1.]
    stdout.p(['Field', 'Value'], positions=positions, after='=')
    stdout.p(['Magazine', issue.magazine.name], positions=positions)
    stdout.p(['Issue', issue.issue], positions=positions)
    stdout.p(['Published on', issue.published_on], positions=positions)

    if issue.links.count() > 0:
        for (i, file), has_next in lookahead(enumerate(issue.links.all())):
            if i == 0:
                stdout.p(['Links', link.link], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', link.link], positions=positions, after='' if has_next else '_')
    else:
        stdout.p(['Links', ''], positions=positions)

    if issue.files.count() > 0:
        for (i, file), has_next in lookahead(enumerate(issue.files.all())):
            if i == 0:
                stdout.p(['Files', 'id: %s, file: %s' % (file.id, file)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', 'id: %s, file: %s' % (file.id, file)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p(['Files', ''], positions=positions)

    if issue.acquisitions.count() > 0:
        for (i, acquisition), has_next in lookahead(enumerate(issue.acquisitions.all())):
            if i == 0:
                stdout.p(['Acquisitions', 'id: %s, date: %s, price: %0.2f' % (acquisition.id, acquisition.date, acquisition.price)], positions=positions, after='' if has_next else '_')
            else:
                stdout.p(['', 'id: %s, date: %s, price: %0.2f' % (acquisition.id, acquisition.date, acquisition.price)], positions=positions, after='' if has_next else '_')
    else:
        stdout.p(['Acquisitions', ''], positions=positions)

    if issue.reads.count() > 0:
        for (i, read), has_next in lookahead(enumerate(issue.reads.all())):
            if i == 0:
                stdout.p(['Read', 'id: %s, date started: %s, date finished: %s' % (read.id, read.started, read.finished)], positions=positions, after='' if has_next else '=')
            else:
                stdout.p(['', 'id: %s, date started: %s, date finished: %s' % (read.id, read.started, read.finished)], positions=positions, after='' if has_next else '=')
    else:
        stdout.p(['Read', ''], positions=positions, after='=')
