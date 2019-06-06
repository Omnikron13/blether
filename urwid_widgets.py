import urwid


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
        if button not in (4, 5):
            return super(SelectionList, self).mouse_event(size, event, button, col, row, focus)
        if button == 4.0:
            for x in range(self.mousescroll):
                self._keypress_up(size)
        if button == 5.0:
            for x in range(self.mousescroll):
                self._keypress_down(size)

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
