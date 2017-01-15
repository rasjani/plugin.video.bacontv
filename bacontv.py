# -*- coding: utf-8 -*-
# vi: set shiftwidth=4 tabstop=4 expandtab:
from xbmcswift2 import Plugin
from xbmcswift2 import xbmcaddon
from xbmcswift2 import xbmc
# from BeautifulSoup import BeautifulSoup as BS
import unicodedata
from urllib2 import HTTPError
from time import sleep
from urlparse import urlparse
from contextlib import closing
import socket
import os
import re
import json
import urllib2
import sqlite3
from urllib import quote_plus
from resources.lib import YouTube,Vimeo, LiveLeak, commands

plugin = Plugin()
BASE_URL = 'http://www.reddit.com'
#BASE_URL = 'http://localhost'
#ADDON_ID = xbmcaddon.getAddonInfo('id')
#ADDON_VERSION = addon.getAddonInfo('version')
ADDON_ID = "plugin.video.bacontv"
ADDON_VERSION = "0.1.0"
SUBREDDITS_DB=xbmc.translatePath("special://profile/addon_data/plugin.video.bacontv/config")
USERDATA_FOLDER=xbmc.translatePath("special://profile/addon_data/plugin.video.bacontv")


if not os.path.isdir(USERDATA_FOLDER):
    os.mkdir(USERDATA_FOLDER)

all_hosters = [YouTube(xbmcaddon, xbmc), Vimeo(xbmcaddon, xbmc), LiveLeak(xbmcaddon,xbmc)]

all_enabled_hosters = filter(lambda hoster: hoster.enabled(), all_hosters)

all_sort_options = [ "cat_new", "cat_hot_hour", "cat_hot_day", "cat_hot_week",
    "cat_hot_month", "cat_top_day", "cat_top_week", "cat_top_month",
    "cat_top_year", "cat_top_all", "cat_com_hour", "cat_com_day",
    "cat_com_week", "cat_com_month", "cat_com_year", "cat_com_all" ]

sort_option_data = {
    "cat_new":              { "sort": "new", "time": "all", "label": [30003] },
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

def normalize(str):
    return  unicodedata.normalize('NFKD', str).encode('ascii','ignore')

@plugin.route("/playvideo/<providername>/<video_id>/")
def playvideo(providername, video_id):
    provider = get_provider_by_name(providername)
    url = provider.resolve_play_url(video_id)
    return plugin.set_resolved_url(url)

def generate_play_link(id, provider, title, date, rating, thumb, description):
    return  {
        'label' : normalize(title),
        'thumbnail' : thumb,
        'path' provider.get_play_url(id),
        'info': {
            'plot': normalize(description)
        },
        'is_playable': True
    }

def get_provider_by_url(url):
    return next((provider for provider in all_enabled_hosters if provider.can_play(url)!=None), None)

def get_provider_by_name(name):
    return next((provider for provider in all_enabled_hosters if provider.name == name), None)

def gen_sites_string():
    return " OR ".join(map(lambda hoster: hoster.site_string, all_enabled_hosters))

def getBoolSetting(opt):
    #return plugin.get_setting(opt) == "true"
    return True

def _(id):
    return plugin.get_string(id)

def _get_sort_label(sort_entry):
    labels = sort_option_data[sort_entry]['label']
    return ": ".join(map(lambda id: _(id), labels))

def cleanTitle(title):
    title = title.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#039;","'").replace("&quot;","\"")
    return title.strip()

enabled_sort_options = filter(lambda opt: getBoolSetting(opt), list(sort_option_data))

def _dlpage(url):
    socket.setdefaulttimeout(30)
    opener = urllib2.build_opener()
    userAgent = "kodi.tv:"+ADDON_ID+":v"+ADDON_VERSION+" (by /u/rasjani)"
    opener.addheaders = [('User-Agent', userAgent)]
    urllib2.install_opener(opener)
    try:
        response = ""
        with closing(urllib2.urlopen(url)) as conn:
            response = conn.read()
        return response
    except Exception as e:
        pass
    return None

def _apicall(url):
    content = _dlpage(url)
    if content != None:
        content = json.loads(content.replace('\\"', '\''))
    return content

def openDatabase():
    #TODO: Error handling
    create = not os.path.exists(SUBREDDITS_DB)
    connection = sqlite3.connect(SUBREDDITS_DB)
    cursor = connection.cursor()
    if create:
        cursor.executescript(commands['INITDB'])
        connection.commit()

    return {'cur': cursor, 'con': connection }

def subreddits():
    cd = openDatabase()
    res = cd['cur'].execute(commands['SUBREDDITS'])
    #TODO: Error handling
    #TODO: check how unicode works in xbmc?
    return map(lambda sub: str(sub[0]), res.fetchall())

def generate_search_url(subreddit, sorting, sites = None):
    # urlMain+"/r/"+subreddit+"/search.json?q="+nsfw+hosterQuery+"&sort=hot&restrict_sr=on&limit="+itemsPerPage+"&t=hour
# https://www.reddit.com/r/suomirap/search.json?q=nsfw:1+site%3Ayoutube.com+OR+site%3Ayoutu.be+OR+site%3Avimeo.com&sort=new&restrict_sr=on&limit=25
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
        # quote_plus("nsfw:yes"),
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
    content = _apicall(url)
    itemlist = []
    if content != None:
        for entry in content['data']['children']:
            title = cleanTitle(entry['data']['title'])
            try:
                description = cleanTitle(entry['data']['media']['oembed']['description'])
            except:
                description = ""
            try:
                date = str(entry['data']['created_utc'])
                date = date.split(".")[0]
                dateTime = str(datetime.datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d %H:%M'))
                date = dateTime.split(" ")[0]
            except:
                date = ""
                dateTime = ""
            ups = entry['data']['ups']
            downs = entry['data']['downs']
            rating = 100
            if ups+downs>0:
                rating = int(ups*100/(ups+downs))
            comments = entry['data']['num_comments']
            #if filter and (ups+downs) > filterThreshold and rating < filterRating:
            #    continue
            try:
                thumb = entry['data']['media']['oembed']['thumbnail_url']
            except:
                thumb = entry['data']['thumbnail']
            try:
                url = entry['data']['media']['oembed']['url']
            except:
                url = urllib2.unquote(entry['data']['url'])

            provider = get_provider_by_url(url)
            play_data = provider.get_play_data(url)

            # TODO: translations for this
            prefix = unicode(dateTime+"  |  "+str(ups+downs)+" votes: "+str(rating)+"% Up  |  "+str(comments)+" comments | Source  " + provider.header + " \n")
            description = prefix + description
            item = generate_play_link(play_data['video_id'], provider, title, date, rating, thumb, description)
            if item != None:
                itemlist.append(item)

        return plugin.finish(itemlist)

@plugin.route("/listsorting/<subreddit>/", name="default_listsorting", options={"sites": None})
@plugin.route("/listsorting/<subreddit>/<sites>/")
def listsorting(subreddit, sites):
    items = []
    for sort_entry in all_sort_options:
        if sort_entry in enabled_sort_options:
            plugin_path = None
            if sites == None:
                sites = gen_sites_string()

            items.append({
                'label': _get_sort_label(sort_entry),
                #'path': plugin.url_for('default_listvideos', subreddit = subreddit, sorting = sort_entry  ),
                'path': plugin.url_for('listvideos', subreddit = subreddit, sorting = sort_entry, sites = sites),
                'is_playable': False
            })

    return plugin.finish(items)

@plugin.route("/")
def index():
    items = []
    for sub in subreddits():
        items.append({
            'label': "/r/" + sub,
            'path': plugin.url_for('default_listsorting', subreddit=sub),
            'is_playable': False
        })
    for site in all_enabled_hosters:
        items.append({
            'label': site.header,
            'path': plugin.url_for('listsorting',subreddit='all', sites=site.site_string),
            'is_playable': False
        })
    items.append({
        'label': 'liveleak',
        'path': plugin.url_for('playvideo', providername='bacontv', video_id='foobar'),
        'is_playable': False
    })
    return plugin.finish(items)

if __name__ == '__main__':
    plugin.run()
