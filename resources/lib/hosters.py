# -*- coding: utf-8 -*-
__author__ = 'rasjani'

class Hoster:
    def __init__(self, header, addon_id, name, setting_name,site_string):
        self.header = header
        self.name = name
        self.setting_name = setting_name
        self.addon_id = addon_id
        self.site_string = site_string

    def getPlayUrl(self):
        return ""

    def getDownloadUrl(self):
        return ""

