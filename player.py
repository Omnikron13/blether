import vlc

from singleton import Singleton
from episode import Episode


class Player(metaclass=Singleton):
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

    def play(self, file):
        media = self.instance.media_new(file.url)
        self.player.set_media(media)
        self.player.play()
