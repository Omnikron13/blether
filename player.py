import vlc

from singleton import Singleton
from episode import Episode


class Player(metaclass=Singleton):
    def __init__(self, loop):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.events = self.player.event_manager()
        self.event_loop = loop

    def play(self, playlist):
        if type(playlist) is Episode:
            media = self.instance.media_new(playlist.url)
            self.player.set_media(media)
            self.player.play()
        else: # Assume iterable representing playlist
            def cb(event):
                # vlc callbacks aren't 'reentrant' so we have to
                # inject the real callback into the main loop
                def defer_cb():
                    # Tag the episode as played at current time(stamp), for future sorting etc.
                    playlist[0].setplayed()

                    Player().play(playlist[1:])

                self.event_loop.alarm(0, defer_cb)

            self.events.event_attach(vlc.EventType.MediaPlayerEndReached, cb)
            media = self.instance.media_new(playlist[0].url)
            self.player.set_media(media)
            self.player.play()
