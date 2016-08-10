# -*- coding: utf-8 -*-

from utils import lookahead, stdout


def show(magazine):
    positions=[.33, 1.]
    stdout.p(['Field', 'Value'], positions=positions, after='=')
    stdout.p(['Name', magazine.name], positions=positions)

    stdout.p(['Journal', magazine.feed], positions=positions)
    stdout.p(['Links', ', '.join([str(l) for l in magazine.links.all()])], positions=positions)
