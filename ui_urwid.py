from functools import reduce

import urwid
from urwid_widgets import SelectionList

from feed import Feed
from episode import Episode


class UI:
    palette = (
        ('normal',   'light gray', 'black',      'default'),
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

        mx = Feed.maxtitlelength()
        columns = urwid.Columns(((mx, cls.feeds_box), cls.episodes_box))
        pile = urwid.Pile((columns, (8, cls.information_box)))

        cls.main_widget = pile

    @classmethod
    def runloop(cls):
        urwid.MainLoop(cls.main_widget, cls.palette, unhandled_input=cls.handle_input).run()

    @classmethod
    def _construct_feeds(cls):
        f = tuple((f.title, f.id) for f in Feed.getall())
        cls.feeds_list = SelectionList('norm', 'focussed', 'selected', f)
        cls.feeds_box = urwid.LineBox(
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
        f = Feed(cls.feeds_list.focus.data)
        episodes = tuple((e.title, e.id) for e in Episode.getbyfeed(f))
        cls.episodes_list.add(episodes)

    @staticmethod
    def handle_input(i):
        if i in ('q', 'Q', 'esc'):
            raise urwid.ExitMainLoop
