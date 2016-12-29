from xbmcswift2 import Plugin
from xbmcswift2 import xbmcaddon
from xbmcswift2 import xbmc
from BeautifulSoup import BeautifulSoup as BS
from urllib2 import HTTPError
from time import sleep
from urlparse import urlparse
import socket
import os
import re
import json
import urllib2
from urllib import quote_plus

plugin = Plugin()

BASE_URL = 'http://www.reddit.com'
#ADDON_ID = xbmcaddon.getAddonInfo('id')
#ADDON_VERSION = addon.getAddonInfo('version')
ADDON_ID = "plugin.video.bacontv"
ADDON_VERSION = "0.1.0"
SUBREDDITS_FILE=xbmc.translatePath("special://profile/addon_data/plugin.video.bacontv/subreddits")
USERDATA_FOLDER=xbmc.translatePath("special://profile/addon_data/plugin.video.bacontv")


if not os.path.isdir(USERDATA_FOLDER):
    os.mkdir(USERDATA_FOLDER)

all_sort_options = [ "cat_new", "cat_hot_hour", "cat_hot_day", "cat_hot_week",
        "cat_hot_month", "cat_top_day", "cat_top_week", "cat_top_month",
        "cat_top_year", "cat_top_all", "cat_com_hour", "cat_com_day",
        "cat_com_week", "cat_com_month", "cat_com_year", "cat_com_all" ]

sort_option_data = {
        "cat_new":              { "sort": "new", "time": None, "label": [30003] },
        "cat_hot_hour":         { "sort": "hot", "time": "hour", "label": [30002,30006] },
        "cat_hot_day":          { "sort": "hot", "time": "day", "label": [30002,30007] },
        "cat_hot_week":         { "sort": "hot", "time": "week", "label": [30002,30008] },
        "cat_hot_month":        { "sort": "hot", "time": "month", "label": [30002,30009] },
        "cat_top_day":          { "sort": "top", "time": "day", "label": [30004,30007] },
        "cat_top_week":         { "sort": "top", "time": "week", "label": [30004,30008] },
        "cat_top_month":        { "sort": "top", "time": "month", "label": [30004,30009] },
        "cat_top_year":         { "sort": "top", "time": "year", "label": [30004,30010] },
        "cat_top_all":          { "sort": "top", "time": "all", "label": [30004,30011] },
        "cat_com_hour":         { "sort": "comments", "time": "hour", "label": [30005,30006] },
        "cat_com_day":          { "sort": "comments", "time": "day", "label": [30005,30007] },
        "cat_com_week":         { "sort": "comments", "time": "week", "label": [30005,30008] },
        "cat_com_month":        { "sort": "comments", "time": "month", "label": [30005,30009] },
        "cat_com_year":         { "sort": "comments", "time": "year", "label": [30005,30010] },
        "cat_com_all":          { "sort": "comments", "time": "all", "label": [30005,30011] }}

#items_per_page = int(xbmcaddon.getSetting("itemsPerPage"))
items_per_page = 0
items_per_page = ["25", "50", "75", "100"][items_per_page]

def getBoolSetting(opt):
        #xbmcaddon.getSetting(opt) == "true"
        return True

def _(id):
        #return xbmcaddon.getLocalizedString(id).encode('utf-8')
        return str(id).encode('utf-8')

def _get_sort_label(sort_entry):
        labels = sort_option_data[sort_entry]['label']
        return ": ".join(map(lambda id: _(id), labels))

enabled_sort_options = filter(lambda opt: getBoolSetting(opt), list(sort_option_data))


print _get_sort_label("cat_hot_hour")
def _apicall(url):
    socket.setdefaulttimeout(30)
    opener = urllib2.build_opener()
    userAgent = "KODI | " + ADDON_ID + " | " + ADDON_VERSION
    opener.addheaders = [('User-Agent', userAgent)]
    try:
        response = ""
        with urllib2.urlopen(url) as conn:
            response = conn.read()
        return json.loads(response.replace('\\"', '\''))
    except:
        pass
    return none

def subreddits():
    return ["all","Videos","artisanvideos","suomirap"]

def generate_search_url(subreddit, sorting, sites = None):
        # urlMain+"/r/"+subreddit+"/search.json?q="+nsfw+hosterQuery+"&sort=hot&restrict_sr=on&limit="+itemsPerPage+"&t=hour
        data = {
                "base": BASE_URL,
                "subreddit": subreddit,
                "options": "",
                "querystring": "",
        }

        options = {
                'sort' : sort_option_data[sorting]['sort'],
                'restrict_sr': 'on',
                'limit': items_per_page
        }
        time_interval = sort_option_data[sorting]['time']
        if time_interval != None:
                options['t'] = time_interval
        data['options']="&".join(['{}={}'.format(k,v) for k,v in options.iteritems()])


        querystring = [
                "nsfw:1",
        ]
        if sites:
                querystring.append(quote_plus(sites))
        else:
                pass # TODO: Generate query string here?
        data['querystring'] = "+".join(querystring)


        #data['options']

        return "{base}/r/{subreddit}/search.json?q={querystring}&{options}".format(**data)

@plugin.route("/listvideos/<subreddit>/<sorting>", name="default_listvideos", options={"sites": None})
@plugin.route("/listvideos/<subreddit>/<sorting>/<sites>")
def listvideos(subreddit, sorting, sites):
        url = generate_search_url(subreddit, sorting, sites)
        print url
        return []

@plugin.route("/listsorting/<subreddit>/")
def listsorting(subreddit):
    items = []
    for sort_entry in enabled_sort_options:
        items.append({
            'label': _get_sort_label(sort_entry),
            #'path': plugin.url_for('default_listvideos', subreddit = subreddit, sorting = sort_entry  ),
            'path': plugin.url_for('listvideos', subreddit = subreddit, sorting = sort_entry, sites = 'site:youtube.com OR site:youtu.be'),
            'is_playable': False,
            'is_folder': True
        })
        
    return items

@plugin.route("/")
def index():
    items = []
    for sub in subreddits():
        items.append({
            'label': "/r/" + sub,
            'path': plugin.url_for('listsorting', subreddit=sub),
            'is_playable': False,
            'is_folder': True
        })
    return items

if __name__ == '__main__':
    plugin.run()
