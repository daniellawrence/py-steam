#!/usr/bin/env python
# from .api import SteamAPI


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
