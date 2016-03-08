#!/usr/bin/env python
import json

import requests

from .user import SteamUser
from .game import Game


class SteamAPI(object):

    BASE_URL = "http://api.steampowered.com/{steam_object}/{endpoint}/{version}?key={key}"

    cache = {}

    def __init__(self, key):
        self.key = key

    def get(self, steam_object, endpoint, version='v0001', **kwargs):
        cache_key = "{}:{}".format(endpoint, kwargs)
        if cache_key in self.cache:
            return self.cache.get(cache_key)

        key = self.key
        url = self.BASE_URL.format(**locals())
        query_string_list = ["{}={}".format(key,value) for (key, value) in kwargs.items()]
        url = "{}&{}".format(url, "&".join(query_string_list))
        r = requests.get(url)
        j = r.json()
        self.cache[cache_key] = j

        return j

    def get_game(self, app_id):
        cache_key = "app_id:{}".format(app_id)
        if cache_key in self.cache:
            return self.cache.get(cache_key)

        url = "http://store.steampowered.com/api/appdetails/?appids={}".format(app_id)
        r = requests.get(url)
        j = r.json()
        self.cache[cache_key] = j
        return j

    def __repr__(self):
        return "<SteamAPI:{.key}>".format(self)

    def SteamUser(self, steam_id):
        return SteamUser(steam_id=steam_id, steam_api=self)

    def User(self, steam_id):
        return self.SteamUser(steam_id)

    def Game(self, app_id, owner=None):
        return Game(app_id=app_id, steam_api=self, owner=owner)
