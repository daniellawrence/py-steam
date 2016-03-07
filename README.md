py-steam
--------

Simple and Clean interface to the steam api.


overview
--------

`SteamAPI` object holds the api `key`, this uses `requests` to hit the steam api.
Other objects like `Game` & `SteamUser` are the interface to the games and users.

Example: Basic object usage
---------------------------

    >>> steam_id = '76561197965093840'
    >>> print SteamAPI(key).User(steam_id)
    <SteamUser:76561197965093840>

OR

    >>> steam_id = '76561197965093840'
    >>> print User(steam_id, steam_api=SteamAPI(key))
    <SteamUser:76561197965093840>
    

Example: printing details about the user
----------------------------------------

    >>> steam_id = '76561197965093840'
    >>> print SteamAPI(key).User(steam_id).personaname
    JEST3R

Example: print the name of a game on a users name list
----------------------------------------------------

    >>> for _ in SteamAPI(key).User(steam_id).get_games_list():
    ...     print "app_id={0.app_id} name={0.name}".format(game)
    ...     break
    app_id=10 name=Counter-Strike
