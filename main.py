#!/usr/bin/env python
import json

import requests


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


class Game(object):

    def __init__(self, app_id, steam_api=None, owner=None):
        self.app_id = int(app_id)
        self.owner = owner
        self.steam_api = steam_api
        if not self.steam_api and owner and owner.steam_api:
            self.steam_api = owner.steam_api
        if not self.steam_api:
            self.steam_api = SteamAPI(None)

        self._detail_items = [
            u'steam_appid', u'achievements', u'price_overview', u'ext_user_account_notice',
            u'platforms', u'detailed_description', u'screenshots', u'genres', u'required_age',
            u'metacritic', u'about_the_game', u'developers', u'type', u'supported_languages',
            u'website', u'publishers', u'pc_requirements', u'recommendations', u'is_free', u'legal_notice',
            u'background', u'packages', u'categories', u'support_info', u'name', u'package_groups',
            u'release_date', u'movies', u'linux_requirements', u'mac_requirements', u'header_image'
        ]
        self._details = None

    @staticmethod
    def new(app_ids):
        for _id in app_ids:
            yield Game(_id)

    def __repr__(self):
        return '<Game:{.app_id}>'.format(self)

    def __getattr__(self, key):
        if key in self._detail_items:
            self._details = self.get_details()
            return self._details.get(key)

        return super(Game, self).__getattribute__(key)()

    def get_details(self, app_id=None):
        if app_id:
            self.app_id = int(app_id)

        if self._details:
            return self._details

        j = self.steam_api.get_game(self.app_id)
        self._details = j[str(self.app_id)]['data']
        return self._details


class SteamUser(object):

    def __init__(self, steam_id=None, steam_api=None, **kwargs):
        self.steam_id = steam_id
        self.steam_api = steam_api
        self.__dict__.update(**kwargs)
        self._friends = None
        self._games = None
        self._profile_data = None
        self._profile_data_items = [
            u'steamid', u'primaryclanid', u'realname', u'personaname',
            u'personastate', u'personastateflags', u'communityvisibilitystate',
            u'loccountrycode', u'profilestate', u'profileurl', u'timecreated',
            u'avatar', u'commentpermission', u'avatarfull', u'avatarmedium',
            u'lastlogoff'
        ]

    @property
    def friends(self, steam_id=None):
        if self._friends:
            return self._friends
        self._friends = self.get_friends_list(steam_id=steam_id)
        return self._friends

    def Game(self, app_id):
        return Game(app_id=app_id, steam_api=self.steam_api, owner=self)

    @property
    def games(self):
        if self._games:
            return self._games
        self._games = self.get_games_list()
        return self._games

    @property
    def games_set(self):
        return set([_.app_id for _ in self.games])

    def _profile_property_wrapper(self, profile_data, key):
        if self._profile_data:
            return self._profile_data.get(key)
        self._profile_data = profile_data
        return self._profile_data.get(key)

    def __getattr__(self, key):
        if key in self._profile_data_items:
            self._profile_data = self.get_profile()
            return self._profile_data.get(key)

        return super(SteamUser, self).__getattribute__(key)()

    def get_profile(self, steam_id=None):
        if self._profile_data:
            return self._profile_data

        if steam_id:
            self.steam_id = steam_id

        response_json = self.steam_api.get(
            'ISteamUser', 'GetPlayerSummaries',
            version='v0002', steamids=self.steam_id
        )

        # Make this better
        return response_json.get('response', {}).get('players', [])[0]

    def get_friends_list(self, steam_id=None):
        if steam_id:
            self.steam_id = steam_id

        response_json = self.steam_api.get('ISteamUser', 'GetFriendList', steamid=self.steam_id)
        for friend in response_json.get('friendslist', {}).get('friends', []):
            yield SteamUser(
                steam_id=friend.get('steamid'),
                steam_api=self.steam_api,
                friend_since=friend.get('friend_since')
            )

    def get_games_list(self, steam_id=None):
        if steam_id:
            self.steam_id = steam_id

        game_list = self.steam_api.get(
            'IPlayerService', 'GetOwnedGames',
            steamid=self.steam_id
        )
        for game in game_list.get('response', {}).get('games', []):
            yield Game(app_id=game.get('appid'), owner=self)

    def __repr__(self):
        return "<SteamUser:{.steam_id}>".format(self)


# if __name__ == '__main__':
    # steam_id_1 = '76561197960435530'
    # steam_id_2 = '76561197960435531'
    # steam_id_1 = '76561197965093840'
    # print SteamAPI(key).User(steam_id_1)
    # exit(1)
    # print SteamUser(steam_id, SteamAPI(key)).profileurl
    # for game in SteamAPI(key).User(steam_id_1).get_games_list():
    #    print "app_id={0.app_id} name={0.name}".format(game)
    #    break
    # print Game(371660).get_details()
    # exit()
    # print SteamAPI(key).Game(371660).name
    #print SteamAPI(key).User(steam_id).Game(371660).name

    # player_1_games = SteamAPI(key).User(steam_id_1).games_set
    # player_2_games = SteamAPI(key).User(steam_id_2).games_set
    # games = player_1_games & player_2_games
    # print [_.name for _ in Game.new(games)]
