from functools import reduce

import urwid

from singleton import Singleton
from feed import Feed
from episode import Episode
from urwid_widgets import(
    SelectionList,
    PackableLineBox,
    EditDialogue,
    InformationDialogue,
)
from player import Player


class UI(metaclass=Singleton):
    palette = (
        ('normal',   'light gray', 'black',      'default'),
        ('reversed', 'black',      'light gray', 'default'),
        ('selected', 'black',      'dark blue',  'default'),
        ('focussed', 'black',      'light blue', 'default'),
    )

    def __init__(self):
        self.main_widget     : urwid.Widget
        self.feeds_box       : urwid.Widget
        self.feeds_list      : SelectionList
        self.episodes_box    : urwid.Widget
        self.episodes_list   : SelectionList
        self.information_box : urwid.Widget
        self.loop            : urwid.AsyncioEventLoop

        self._construct_feeds()
        self._construct_episodes()
        self._construct_information()

        columns = urwid.Columns((('pack', self.feeds_box), self.episodes_box))
        pile = MainWidget((columns, (8, self.information_box)))

        self.main_widget = pile

        # Without this the episode list starts blank rather than being
        # populated from the first feed in the feeds list.
        # TODO: move into SelectionList method?
        urwid.signals.emit_signal(self.feeds_list.listwalker, 'modified')

    def _construct_feeds(self):
        f = tuple((f.title, f.id) for f in Feed.getall())
        self.feeds_list = SelectionList('norm', 'focussed', 'selected', f)
        self.feeds_box = PackableLineBox(
            self.feeds_list,
            'Feeds',
            lline=None,
            rline=None,
            bline=None,
            tlcorner='─',
            trcorner='─'
        )
        # Selecting a different feed needs to update the episode list
        urwid.connect_signal(
            self.feeds_list.listwalker,
            'modified',
            self._feeds_modified_cb
        )

    def _construct_episodes(self):
        self.episodes_list = EpisodesList('norm', 'focussed', 'selected')
        self.episodes_box = urwid.LineBox(
            self.episodes_list,
            'Episodes',
            rline=None,
            bline=None,
            tlcorner='┬',
            trcorner='─'
        )
        urwid.connect_signal(
            self.episodes_list.listwalker,
            'modified',
            self._episodes_modified_cb
        )

    def _construct_information(self):
        self.information_box = urwid.LineBox(
            urwid.SolidFill('~'), # TODO: replace this placeholder
            'Information',
            lline=None,
            rline=None,
            bline=None,
            tlcorner='─',
            trcorner='─'
        )


    def runloop(self):
        self.loop = urwid.MainLoop(
            self.main_widget,
            self.palette,
            # This event loop plays nicer with vlc callbacks
            event_loop=urwid.AsyncioEventLoop(),
            unhandled_input=self.handle_input,
        )
        self.loop.run()

    @classmethod
    def addfeeddialogue(cls):
        EditDialogue(
            'Edit Test',
            UI.loop,
            lambda t: UI.addfeed(t),
            attr='reversed',
            edit_attr='normal',
        ).display()

    @classmethod
    def addfeed(cls, url):
        try:
            f = Feed.add(url)
            cls.feeds_list.add(f.title, f.id)
        except Feed.Error as e:
            cls.infodialogue(
                'Error Adding Feed',
                e.__str__(),
            )

    @classmethod
    def infodialogue(cls, title, message):
        InformationDialogue(
            title,
            message,
            cls.loop,
            attr='reversed',
        ).display()

    @classmethod
    def _feeds_modified_cb(cls):
        if not cls.feeds_list.selected:
            return
        # TODO: add support for special non-id entries (like e.g. 'All')
        f = Feed(cls.feeds_list.selected.data)
        cls.episodes_list.display(Episode.getbyfeed(f))

    @classmethod
    def _episodes_modified_cb(cls):
        pass

    @staticmethod
    def handle_input(i):
        pass


class MainWidget(urwid.Pile):
    def keypress(self, size, key):
        if key in ('q', 'esc'):
            raise urwid.ExitMainLoop
        elif key is 'a':
            UI.addfeeddialogue()
        elif key is 'p':
            p = Player(UI.loop.event_loop)
            # Play from the selected episode to the last episode
            i = UI.episodes_list.data.index(UI.episodes_list.selected.data)
            p.play(UI.episodes_list.data[i:])
        else:
            return super().keypress(size, key)


class EpisodesList(SelectionList):
    def display(self, episodes):
        self.clear()
        for e in episodes:
            self.add(e.title, e)
