import vlc

from singleton import Singleton


class Player(metaclass=Singleton):
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

    def play(self, file):
        media = self.instance.media_new(file)
        self.player.set_media(media)
        self.player.play()
