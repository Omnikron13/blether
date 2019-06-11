from functools import reduce

import urwid

from feed import Feed
from episode import Episode
from urwid_widgets import(
    SelectionList,
    PackableLineBox,
    EditDialogue,
    InformationDialogue,
)
from player import Player


class UI:
    palette = (
        ('normal',   'light gray', 'black',      'default'),
        ('reversed', 'black',      'light gray', 'default'),
        ('selected', 'black',      'dark blue',  'default'),
        ('focussed', 'black',      'light blue', 'default'),
    )

    @classmethod
    def construct(cls):
        if hasattr(cls, 'feeds_list'):
            return
        cls._construct_feeds()
        cls._construct_episodes()
        cls._construct_information()

        columns = urwid.Columns((('pack', cls.feeds_box), cls.episodes_box))
        pile = MainWidget((columns, (8, cls.information_box)))

        cls.main_widget = pile

        # Without this the episode list starts blank rather than being
        # populated from the first feed in the feeds list.
        # TODO: move into SelectionList method?
        urwid.signals.emit_signal(cls.feeds_list.listwalker, 'modified')

    @classmethod
    def runloop(cls):
        cls.loop = urwid.MainLoop(
            cls.main_widget,
            cls.palette,
            unhandled_input=cls.handle_input
        )
        cls.loop.run()

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
    def _construct_feeds(cls):
        f = tuple((f.title, f.id) for f in Feed.getall())
        cls.feeds_list = SelectionList('norm', 'focussed', 'selected', f)
        cls.feeds_box = PackableLineBox(
            cls.feeds_list,
            'Feeds',
            lline=None,
            rline=None,
            bline=None,
            tlcorner='─',
            trcorner='─'
        )
        # Selecting a different feed needs to update the episode list
        urwid.connect_signal(
            cls.feeds_list.listwalker,
            'modified',
            cls._feeds_modified_cb
        )

    @classmethod
    def _construct_episodes(cls):
        cls.episodes_list = EpisodesList('norm', 'focussed', 'selected')
        cls.episodes_box = urwid.LineBox(
            cls.episodes_list,
            'Episodes',
            rline=None,
            bline=None,
            tlcorner='┬',
            trcorner='─'
        )
        urwid.connect_signal(
            cls.episodes_list.listwalker,
            'modified',
            cls._episodes_modified_cb
        )

    @classmethod
    def _construct_information(cls):
        cls.information_box = urwid.LineBox(
            urwid.SolidFill('~'), # TODO: replace this placeholder
            'Information',
            lline=None,
            rline=None,
            bline=None,
            tlcorner='─',
            trcorner='─'
        )

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
        if key in ('q', 'Q', 'esc'):
            raise urwid.ExitMainLoop
        elif key in ('a', 'A'):
            UI.addfeeddialogue()
        elif key in ('p', 'P'):
            p = Player()
            p.play(Episode(UI.episodes_list.selected.data).url)
        else:
            return super().keypress(size, key)


class EpisodesList(SelectionList):
    def display(self, episodes):
        self.clear()
        for e in episodes:
            self.add(e.title, e.id)
