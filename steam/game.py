#!/usr/bin/env python
# from .api import SteamAPI


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
