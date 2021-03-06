# -*- coding: utf-8 -*-
# vi: set shiftwidth=4 tabstop=4 expandtab:
__author__ = 'rasjani'

from contextlib import closing
import unicodedata
import socket
import json
from urllib2 import HTTPError
from urllib2 import build_opener, install_opener, urlopen

def normalize(str):
    return  unicodedata.normalize('NFKD', str).encode('ascii','ignore')

def generate_play_link(id, provider, title, date, rating, thumb, description):
    return  {
        'label' : normalize(title),
        'thumbnail' : thumb,
        'path': provider.get_play_url(id),
        'info': {
            'plot': normalize(description)
        },
        'is_playable': True
    }

def clean_title(title):
    title = title.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#039;","'").replace("&quot;","\"")
    return title.strip()


def dl_page(url, userAgent = None, extra_headers = None, default_timeout = 30):
    socket.setdefaulttimeout(default_timeout)
    if userAgent != None or extra_headers != None:
        opener = build_opener()
        headers = []

        if userAgent != None:
            headers.append( ('User-Agent', userAgent ) )

        if extra_headers != None:
            headers.append(extra_headers)

        opener.addheaders = headers
        install_opener(opener)

    try:
        response = ""
        with closing(urlopen(url)) as conn:
            response = conn.read()
        return response
    except Exception as e:
        pass
    return None


def api_call(url, userAgent = None):
    content = dl_page(url, userAgent)
    if content != None:
        content = json.loads(content.replace('\\"', '\''))
    return content
