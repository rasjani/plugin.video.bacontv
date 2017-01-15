# -*- coding: utf-8 -*-
# vi: set shiftwidth=4 tabstop=4 expandtab:
__author__ = 'rasjani'
import re

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

    def get_play_url(self, id):
        return self.play_template.format(self.addon_id, id)


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
                    'play_url': self.get_play_url(videoid),
                    'dl_url': self.get_download_url(videoid)
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
                "plugin://{0}/play/?video_id={1}")
