import vlc

from singleton import Singleton


class Player(metaclass=Singleton):
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
