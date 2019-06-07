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
        pile = urwid.Pile((columns, (8, cls.information_box)))

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
        cls.episodes_list = SelectionList('norm', 'focussed', 'selected')
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
        cls.episodes_list.clear()
        if not cls.feeds_list.focus:
            return
        # TODO: add support for special non-id entries (like e.g. 'All')
        f = Feed(cls.feeds_list.focus.data)
        episodes = tuple((e.title, e.id) for e in Episode.getbyfeed(f))
        cls.episodes_list.add(episodes)

    @classmethod
    def _episodes_modified_cb(cls):
        pass

    @staticmethod
    def handle_input(i):
        if i in ('q', 'Q', 'esc'):
            raise urwid.ExitMainLoop
