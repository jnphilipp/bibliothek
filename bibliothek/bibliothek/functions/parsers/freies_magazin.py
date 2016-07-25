# -*- coding: utf-8 -*-

import re

from datetime import datetime
from django.core.files.base import ContentFile
from files.models import File
from links.models import Link
from magazines.models import Magazine, Issue
from shelves.models import Acquisition, Read
from urllib.error import HTTPError
from utils import stdout

from .base import RSSParser, HTMLParser


class FreiesMagazinRSSParser(RSSParser):
    def __init__(self, user_agent=None):
        super(FreiesMagazinRSSParser, self).__init__()
        self.base_issue_url = 'http://www.freiesmagazin.de/freiesMagazin-%(year)s-%(month)s'
        self.base_cover_url = 'http://www.freiesmagazin.de/system/files/freiesmagazin-%(year)s-%(month)s.png'
        self.base_pdf_url = 'http://www.freiesmagazin.de/ftp/%(year)s/freiesMagazin-%(year)s-%(month)s.pdf'
        self.base_epub_bilder_url = 'http://www.freiesmagazin.de/ftp/%(year)s/freiesMagazin-%(year)s-%(month)s-bilder.epub'
        self.magazine = Magazine.objects.get(name='freiesMagazin')


    def fetch(self):
        rssfeed = super(FreiesMagazinRSSParser, self).fetch(self.magazine.feed.link)

        html = HTMLParser()
        for entry in reversed(rssfeed.entries):
            match = re.search(r'freiesMagazin\s(?P<month>[0-9]+)\/(?P<year>[0-9]+)\serschienen', entry.title)
            if match:
                month = match.group('month')
                year = match.group('year')
                issue_dict = {'month':month, 'year':year}

                try:
                    issue = Issue.objects.get(magazine=self.magazine, issue='%(month)s/%(year)s' % issue_dict)
                    stdout.p(['Issue %(month)s/%(year)s already exists.' % issue_dict], after='=')
                except Issue.DoesNotExist:
                    issue = Issue.objects.create(magazine=self.magazine, issue='%(month)s/%(year)s' % issue_dict)
                    issue.published_on =  datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z').date()

                    link, created = Link.objects.get_or_create(link=self.base_issue_url % issue_dict)
                    issue.links.add(link)

                    try:
                        issue.cover_image.save('cover.png', ContentFile(html.fetch(self.base_cover_url % issue_dict)))
                    except HTTPError as e:
                        stdout.p(['No cover image found.'], positions=[1.])

                    try:
                        file_obj = File()
                        file_obj.file.save('freiesMagazin-%(year)s-%(month)s.pdf' % issue_dict, ContentFile(html.fetch(self.base_pdf_url % issue_dict)))
                        file_obj.content_object = issue
                        file_obj.save()
                    except HTTPError as e:
                        stdout.p(['No PDF file found.'], positions=[1.])

                    try:
                        file_obj = File()
                        file_obj.file.save('freiesMagazin-%(year)s-%(month)s.epub' % issue_dict, ContentFile(html.fetch(self.base_epub_bilder_url % issue_dict)))
                        file_obj.content_object = issue
                        file_obj.save()
                    except HTTPError as e:
                        stdout.p(['No EPUB file found.'], positions=[1.])

                    issue.save()
                    stdout.p(['New issue added %(month)s/%(year)s' % issue_dict], positions=[1.])

                    acquisition = Acquisition.objects.create(date=datetime.today().date(), content_object=issue)
                    stdout.p(['Successfully added acquisition on "%s".' % acquisition.date], positions=[1.])
                    read = Read.objects.create(started=datetime.today().date(), content_object=issue)
                    stdout.p(['Successfully added read started on "%s".' % read.started], after='=', positions=[1.])


    def archive(self):
        html = HTMLParser()
        for year in range(2006, datetime.today().year + 1):
            for month in range(3 if year == 2006 else 1, datetime.today().month if datetime.today().year == year else 13):
                issue_dict = {'month':'%02d' % month, 'year':year}

                try:
                    data = html.fetch(self.base_pdf_url % issue_dict)

                    try:
                        issue = Issue.objects.get(magazine=self.magazine, issue='%(month)s/%(year)s' % issue_dict)
                        stdout.p(['Issue %(month)s/%(year)s already exists.' % issue_dict], after='=', positions=[1.])
                    except Issue.DoesNotExist:
                        issue = Issue.objects.create(magazine=self.magazine, issue='%(month)s/%(year)s' % issue_dict)
                        issue.published_on = datetime(year, int(month), 1).date()

                        link, created = Link.objects.get_or_create(link=self.base_issue_url % issue_dict)
                        issue.links.add(link)

                        try:
                            issue.cover_image.save('cover.png', ContentFile(html.fetch(self.base_cover_url % issue_dict)))
                        except HTTPError as e:
                            stdout.p(['No cover image found.'], positions=[1.])

                        try:
                            file_obj = File()
                            file_obj.file.save('freiesMagazin-%(year)s-%(month)s.pdf' % issue_dict, ContentFile(html.fetch(self.base_pdf_url % issue_dict)))
                            file_obj.content_object = issue
                            file_obj.save()
                        except HTTPError as e:
                            try:
                                file_obj = File()
                                file_obj.file.save(('freiesMagazin-%(year)s-%(month)s.pdf' % issue_dict).replace('/ftp', ''), ContentFile(html.fetch(self.base_pdf_url % issue_dict)))
                                file_obj.content_object = issue
                                file_obj.save()
                            except HTTPError as e:
                                stdout.p(['No PDF file found.'], positions=[1.])

                        try:
                            file_obj = File()
                            file_obj.file.save('freiesMagazin-%(year)s-%(month)s.epub' % issue_dict, ContentFile(html.fetch(self.base_epub_bilder_url % issue_dict)))
                            file_obj.content_object = issue
                            file_obj.save()
                            issue.save()
                        except HTTPError as e:
                            stdout.p(['No EPUB file found.'], positions=[1.])

                        stdout.p(['New issue added %(month)s/%(year)s' % issue_dict], positions=[1.])

                        acquisition = Acquisition.objects.create(date=datetime.today().date(), content_object=issue)
                        stdout.p(['Successfully added acquisition on "%s".' % acquisition.date], after='=', positions=[1.])
                except HTTPError as e:
                    pass
