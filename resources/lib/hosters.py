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
from base64 import b64encode
from .tools import dl_page


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

    def _addon_installed(self,id):
        return self.xbmc.getCondVisibility( ('System.HasAddon(%s)' % self.addon_id) )

    def enabled(self):
        return True # TODO: Remove later
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
            ['youtube.com/.*v=([^#\&\?]*).*', 'youtube.com/.*watch\\?v=([^#\&\?]*).*','youtu.be/([^#\&\?]*).*' ],
            #https://www.youtube.com/attribution_link?a=tn9rdwcttpU&amp;u=/watch?v=zQvcni57hRM&feature=share
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
        content = dl_page(url)
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
        content = dl_page(url)
        if content != None:
            match = re.compile("\s+var\s+videoObject\s+=\s+({.*?});", re.DOTALL).findall(content)
            if match:
                # TODO: Error handling
                data = json.loads(match[0])
                return  "https://{0}".format(data['files']['mp4']['embed_url'])

        return None

class GfyCat(Hoster):
    def __init__(self, xbmcaddon, xbmc):
        Hoster.__init__(self, xbmcaddon, xbmc,
            "[ GfyCat.com ]",
            "plugin.video.bacontv",
            "gfycat",
            "show_gfycat",
            "site:gfycat.com",
            ["gfycat.com\/(.*)"],
            "plugin://{0}/playvideo/{2}/{1}"
        )

    def resolve_play_url(self, id):
        url = "http://gfycat.com/cajax/get/{0}".format(id)
        content = dl_page(url).replace('\\"', '\'')
        if content != None:
            content = json.loads(content.replace('\\"','\''))
            if "gfyItem" in content and "mp4Url" in content["gfyItem"]:
                return content["gfyItem"]["mp4Url"]

        return None

class Vidme(Hoster):
    api_key = 'uuBPBDwIJ7JC1g2ZFxg0G8o5yHUjS3IO'
    def __init__(self, xbmcaddon, xbmc):
        Hoster.__init__(self, xbmcaddon, xbmc,
            '[ VidMe.com ]',
            'plugin.video.bacontv',
            'vidme',
            'show_vidme',
            'site:vid.me',
            ['vid\.me/(.+)/.*', 'vid\.me/(.+)'], # TODO: Could be a single re
            'plugin://{0}/playvideo/{2}/{1}'
        )
        self.extra_headers = ('Authorization', 'Basic {0}'.format(b64encode("{0}:".format(self.api_key)))) # I have a feeling that this is not even needed .. 

    def resolve_play_url(self, id):
        def to_json(data):
            return json.loads(data.replace('\\"', '\''))
        url  = "https://api.vid.me/video/{0}".format(id)
        content = dl_page(url, extra_headers=self.extra_headers)
        if content != None:
            content = to_json(content)
            return content['video']['complete_url']
        else:
            url = "https://api.vid.me/videoByUrl?url=https%3A%2F%2Fvid.me%2F{0}".format(id)
            content = dl_page(url, extra_headers=self.extra_headers)
            if content != None:
                content = to_json(content)
                return content['video']['complete_url']
        return None

