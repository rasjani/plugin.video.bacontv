# -*- coding: utf-8 -*-
# vi: set shiftwidth=4 tabstop=4 expandtab:
__author__ = 'rasjani'
import re
from contextlib import closing
from urllib2 import HTTPError
import socket
import urllib2
import urllib
import json


def _dlpage(url):
    socket.setdefaulttimeout(30)
    opener = urllib2.build_opener()
    try:
        response = ""
        with closing(urllib2.urlopen(url)) as conn:
            response = conn.read()
        return response
    except Exception as e:
        pass
    return None

class Hoster:
    def __init__(self, xbmcaddon, xbmc, header, addon_id, name, setting_name,site_string, matchers, play_template):
        self.xbmcaddon = xbmcaddon
        self.xbmc = xbmc
        self.header = header
        self.name = name
        self.setting_name = setting_name
        self.addon_id = addon_id
        self.site_string = site_string
        self.matchers = []
        for restring in matchers:
            self.matchers.append(re.compile(restring, re.DOTALL))
        self.play_template = play_template

    def resolve_play_url(self, id):
        return None

    def get_play_url(self, id):
        return self.play_template.format(self.addon_id, id, self.name)

    def get_download_url(self,id):
        return None

    def _addon_installed(self,id):
        return self.xbmc.getCondVisibility( ('System.HasAddon(%s)' % self.addon_id) )

    def enabled(self):
        return True
        return self.xbmcaddon.getSetting(self.setting_name) == "true" and self._addon_installed()

    def process_video_id(self, video_id):
        return video_id

    def can_play(self, url):
        for compiled_re in self.matchers:
            match = compiled_re.findall(url)
            if match:
                return True
        return None

    def get_play_data(self, url):
        for compiled_re in self.matchers:
            match = compiled_re.findall(url)
            if match:
                videoid =  self.process_video_id(match[0])
                return {
                    'hoster': self.name,
                    'video_id': videoid,
                }
        return None


class YouTube(Hoster):
    def __init__(self, xbmcaddon, xbmc):
        Hoster.__init__(self,xbmcaddon, xbmc,
            "[ YouTube.com ]",
            "plugin.video.youtube",
            "youtube",
            "show_youtube",
            "site:youtube.com OR site:youtu.be",
            ['youtube.com/.*v=([^#\&\?]*).*', 'youtube.com/watch\\?v=([^#\&\?]*).*','youtu.be/([^#\&\?]*).*'],
            "plugin://{0}/play/?video_id={1}"
        )

class Vimeo(Hoster):
    def __init__(self, xbmcaddon, xbmc):
        Hoster.__init__(self,xbmcaddon, xbmc,
            "[ Vimeo.com ]",
            "plugin.video.vimeo",
            "vimeo",
            "show_vimeo",
            "site:vimeo.com",
            ['vimeo.com/\D*(\d+)'],
            "plugin://{0}/play/?video_id={1}"
        )

class LiveLeak(Hoster):
    def __init__(self, xbmcaddon, xbmc):
        Hoster.__init__(self, xbmcaddon, xbmc,
            "[ LiveLeak.com ]",
            "plugin.video.bacontv",
            "liveleak",
            "show_liveleak",
            "site:liveleak.com",
            ["liveleak.com\/.*i=([^#\&\?]*).*"],
            "plugin://{0}/playvideo/{2}/{1}"
        )

    def resolve_play_url(self, id):
        url = "http://www.liveleak.com/view?i={0}&ajax=1".format(id)
        content = _dlpage(url)
        if content != None:
            for matcher in ['hd_file_url=(.+?)&', 'file: "(.+?)"']:
                match = re.compile(matcher, re.DOTALL).findall(content)
                if match:
                    url = urllib.unquote_plus(match[0])
                    return url
            # TODO: <iframe src="http://www.youtube.com/embed/O8DgzgNudHM?rel=0" allowfullscreen="" width="100%" height="480" frameborder="0"></iframe>
            # live-leak pages can actually just embed youtube .. grap tab and return plugin://plugin.video.youtube/play/?video_id=XXX here
        return None


class Streamable(Hoster):
    def __init__(self, xbmcaddon, xbmc):
        Hoster.__init__(self, xbmcaddon, xbmc,
            "[ Streamable.com ]",
            "plugin.video.bacontv",
            "streamable",
            "show_streamable",
            "site:streamable.com",
            ["streamable.com\/(.*)"],
            "plugin://{0}/playvideo/{2}/{1}"
        )

    def resolve_play_url(self, id):
        url = "http://streamable.com/{0}".format(id)
        content = _dlpage(url)
        if content != None:
            match = re.compile("\s+var\s+videoObject\s+=\s+({.*?});", re.DOTALL).findall(content)
            if match:
                # TODO: Error handling
                data = json.loads(match[0])
                return  "https://{0}".format(data['files']['mp4']['embed_url'])

        return None
