import urwid


class SelectionList(urwid.ListBox):
    def __init__(self, attr, focussed_attr, selected_attr, items = None):
        self.attr = attr
        self.focussed_attr = focussed_attr
        self.selected_attr = selected_attr
        self.listwalker = urwid.SimpleFocusListWalker([])
        super().__init__(self.listwalker)
        self.selected = None

        def modified():
            if self.selected:
                self.selected.set_attr_map({None: self.attr})
            self.selected = self.focus
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
