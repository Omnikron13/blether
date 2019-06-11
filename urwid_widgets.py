import urwid

from typing import(
    Tuple,
)

class SelectionList(urwid.ListBox):
    def __init__(self, attr, focussed_attr, selected_attr, items = None, mousescroll=4):
        self.attr = attr
        self.focussed_attr = focussed_attr
        self.selected_attr = selected_attr
        self.listwalker = urwid.SimpleFocusListWalker([])
        self.mousescroll = mousescroll

        super().__init__(self.listwalker)

        self.selected = None

        def modified():
            if self.selected:
                self.selected.set_attr_map({None: self.attr})
            self.selected = self.focus
            if self.selected:
                self.selected.set_attr_map({None: self.selected_attr})

        urwid.connect_signal(self.listwalker, 'modified', modified)
        if items:
            self.add(items)

    @property
    def data(self) -> Tuple:
        return tuple(d.data for d in self.listwalker)

    def add(self, text, data = None):
        if isinstance(text, str):
            sr = self.SelectableRow(text, self.attr, self.focussed_attr, data)
            self.listwalker.append(sr)
        else: # assume iterable; add many
            for i in text:
                self.add(i[0], i[1])

    def clear(self):
        """
        Clears the list held in the underlying list walker
        """
        self.listwalker.clear()

    def pack(self, size, focus=False):
        """
        Calculates packing size based on that of the children.
        Columns is the max() column size of the children, rows is the sum.
        """
        col = 0
        row = 0
        for x in self.listwalker:
            p = x.pack(size)
            col = max(col, p[0])
            row += p[1]
        return col, row

    def mouse_event(self, size, event, button, col, row, focus):
        """
        Mouse events are captured to process scroll-wheel scrolling.
        """
        if button == 4:
            for x in range(self.mousescroll):
                self._keypress_up(size)
        elif button == 5:
            for x in range(self.mousescroll):
                self._keypress_down(size)
        else:
            return super().mouse_event(size, event, button, col, row, focus)

    class SelectableRow(urwid.AttrMap):
        class SelectableText(urwid.Text):
            _selectable = True

            def keypress(self, _, key):
                return key

        @property
        def text(self):
            return self.original_widget.text

        def __init__(self, text, attr, focus, data=None):
            si = self.SelectableText(text)
            super().__init__(si, attr, focus_map=focus)
            self.data = data


class PackableLineBox(urwid.LineBox):
    # TODO: calculate amount of padding needed by sides being used
    def pack(self, size=None, focus=False):
        s = self.original_widget.pack(size, focus)
        return max(s[0], len(self.title_widget.text)+4), s[1]+1


class EditDialogue(urwid.Overlay):
    def __init__(self, title, loop, ok_callback,
        text='',
        align='center',
        width=('relative', 80),
        valign='middle',
        height=4,
        attr=None,
        edit_attr=None,
    ):
        self._loop = loop
        self._main_widget = loop.widget

        def dismiss(button):
            self._loop.widget = self._main_widget

        edit = urwid.Edit(edit_text=text)
        edit_container = urwid.BoxAdapter(urwid.Filler(edit), 1)
        edit_container = urwid.AttrMap(edit_container, edit_attr)

        def ok_callback_wrapper(button, args):
            dismiss(button)
            ok_callback(edit.text)

        ok = urwid.Button('Ok', ok_callback_wrapper, edit)
        ok._label.align = 'center'
        ok = urwid.Padding(ok, align='center', width=10)

        cancel = urwid.Button('Cancel', dismiss)
        cancel._label.align = 'center'
        cancel = urwid.Padding(cancel, align='center', width=10)

        buttons= urwid.Columns((ok, cancel))
        pile = urwid.Pile((edit_container, buttons))
        box = urwid.LineBox(urwid.Filler(pile), title)
        box = urwid.AttrMap(box, attr)

        super().__init__(
            box,
            self._loop.widget,
            align,
            width,
            valign,
            height,
        )

    def display(self):
        self._loop.widget = self


class InformationDialogue(urwid.Overlay):
    def __init__(self, title, message, loop,
                 align='center',
                 width=48,
                 valign='middle',
                 attr=None,
                 ):
        self._loop = loop
        self._main_widget = loop.widget

        message = urwid.Text(message)

        def dismiss(button):
            self._loop.widget = self._main_widget

        ok = urwid.Button('Ok', dismiss)
        ok._label.align = 'center'

        fill = urwid.Filler(message)
        pad = urwid.Padding(ok, align='center', width=10)
        pile = urwid.Pile((fill, ('pack', pad)))
        box = urwid.LineBox(pile, title)
        box = urwid.AttrMap(box, attr)

        super().__init__(
            box,
            self._loop.widget,
            align,
            width,
            valign,
            # height needed by message, plus 3 for buttons & linebox
            message.pack((width-2,))[1] + 3
        )

    def display(self):
        self._loop.widget = self
