# -*- coding: utf-8 -*-
__author__ = 'rasjani'
import re

class Hoster:
    def __init__(self, xbmcaddon, xbmc, header, addon_id, name, setting_name,site_string, matchers):
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


    def get_play_url(self):
        return None

    def get_download_url(self):
        return None

    def _addon_installed(self):
        return self.xbmc.getCondVisibility( ('System.HasAddon(%s)' % self.addon_id) )

    def enabled(self):
        return True
        return self.xbmcaddon.getSetting(self.setting_name) == "true" and self._addon_installed()

    def process_video_id(self, video_id):
        return video_id

    def can_play(self, url):
        for compiled_re in matchers:
            match = compiled_re.findall(url)
            if match != None:
                return {
                    'hoster': self.name,
                    'video_id': self.process_video_id(match[0])
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
                ['youtube.com/watch\\?v=(.+?)"','youtu.be/(.+?)"'])

class Vimeo(Hoster):
    def __init__(self, xbmcaddon, xbmc):
        Hoster.__init__(self,xbmcaddon, xbmc,
                "[ Vimeo.com ]",
                "plugin.video.vimeo",
                "vimeo",
                "show_vimeo",
                "site:vimeo.com",
                ['vimeo.com/(.+?)'])

    def process_video_id(self, video_id):
        return video_id.replace('#','?').split('?')
