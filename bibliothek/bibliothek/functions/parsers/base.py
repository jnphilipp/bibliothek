# -*- coding: utf-8 -*-

import feedparser
import json
import urllib.parse
import urllib.request


# clear out the html element list so all are removed
feedparser._HTMLSanitizer.acceptable_elements = []


class Parser:
    def fetch(self, url):
        pass


class RSSParser(Parser):
    def fetch(self, url):
        return feedparser.parse(url)


class HTMLParser(Parser):
    def __init__(self, user_agent=None):
        super(HTMLParser, self).__init__()
        self.user_agent = user_agent if user_agent else 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'


    def fetch(self, url):
        headers = {'User-Agent': self.user_agent}
        request = urllib.request.Request(urllib.parse.quote(url, ':/?='), headers=headers)
        with urllib.request.urlopen(request) as response:
            content = response.read()
            if 'charset' in response.getheader('Content-Type'):
                encoding = response.getheader('Content-Type').split('charset=', 1)[-1].split('"', 1)[0]
                if encoding:
                    content = content.decode(encoding)
            if 'application/json' in response.getheader('Content-Type'):
                content = json.loads(content)
        return content
