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


def dl_page(url, userAgent = None):
    print "DL_PAGE",1, url
    socket.setdefaulttimeout(30)
    print "DL_PAGE",2
    if userAgent != None:
        print "DL_PAGE",3
        opener = build_opener()
        opener.addheaders = [('User-Agent', userAgent)]
        install_opener(opener)

    print "DL_PAGE",4
    try:
        response = ""
        with closing(urlopen(url)) as conn:
            response = conn.read()
        return response
    except Exception as e:
        print "DL_PAGE", e
        pass
    return None


def api_call(url, userAgent = None):
    print "APICALL",1
    content = dl_page(url, userAgent)
    print "APICALL",2
    if content != None:
        print "APICALL",3
        content = json.loads(content.replace('\\"', '\''))
        print "APICALL",4
    return content
