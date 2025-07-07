class Element:
    def __init__(self, name, x=0, y=0, width=100, height=30, selectable=True, text=""):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.selectable = selectable
        self.selected = False
        self.children = []
        self.parent = None
        self._signals = {}
        self.text = text  # Unified text property

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def get_path_names(self):
        return [node.name for node in self.get_path()]

    def get_path(self):
        path = []
        node = self
        while node:
            path.append(node)
            node = node.parent
        return list(reversed(path))

    def print_focus(self):
        print("Focused:", " > ".join(self.get_path_names()))

    def get_selectable_children(self):
        return [c for c in self.children if c.selectable]

    def find_next(self):
        if not self.parent:
            return self
        siblings = self.parent.get_selectable_children()
        if self not in siblings:
            # If this element is not selectable, find the first selectable sibling
            return siblings[0] if siblings else self
        idx = siblings.index(self)
        if idx + 1 < len(siblings):
            return siblings[idx + 1]
        return self

    def find_prev(self):
        if not self.parent:
            return self
        siblings = self.parent.get_selectable_children()
        if self not in siblings:
            # If this element is not selectable, find the last selectable sibling
            return siblings[-1] if siblings else self
        idx = siblings.index(self)
        if idx - 1 >= 0:
            return siblings[idx - 1]
        return self

    def focus_next(self):
        next_elem = self.find_next()
        if next_elem is not self:
            next_elem.selected = True
            self.selected = False
            # next_elem.print_focus()
            return next_elem
        return self

    def focus_prev(self):
        prev_elem = self.find_prev()
        if prev_elem is not self:
            prev_elem.selected = True
            self.selected = False
            # prev_elem.print_focus()
            return prev_elem
        return self

    def focus_child(self):
        selectable = self.get_selectable_children()
        if selectable:
            self.selected = False
            selectable[0].selected = True
            selectable[0].print_focus()
            return selectable[0]
        return self

    def focus_parent(self):
        if self.parent and self.parent.selectable:
            self.selected = False
            self.parent.selected = True
            self.parent.print_focus()
            return self.parent
        return self

    def on_key(self, event):
        # Default: do nothing
        pass

    def render(self, surface, path, font, x=None, y=None, width=None, height=None):
        # Use instance's own geometry if not provided
        x = self.x if x is None else x
        y = self.y if y is None else y
        width = self.width if width is None else width
        height = self.height if height is None else height
        # Panels and leaf elements will override this
        pass

    def connect(self, signal_name, callback):
        if signal_name not in self._signals:
            self._signals[signal_name] = []
        self._signals[signal_name].append(callback)

    def emit(self, signal_name, *args, **kwargs):
        for cb in self._signals.get(signal_name, []):
            cb(*args, **kwargs)

    def render_text(self, surface, font, x, y, width, height, color=(255,255,255), padding=10):
        """Render self.text, truncated to fit width unless selected."""
        if not self.text:
            return
        text = self.text
        if self.selected:
            # Always render full text if selected
            rendered_text = text
        else:
            # Truncate text to fit width
            rendered_text = text
            while font.size(rendered_text)[0] > width - 2 * padding and len(rendered_text) > 0:
                rendered_text = rendered_text[:-1]
            if rendered_text != text and len(rendered_text) > 3:
                rendered_text = rendered_text[:-3] + "..."
        text_surface = font.render(rendered_text, True, color)
        surface.blit(
            text_surface,
            (x + padding, y + height // 2 - text_surface.get_height() // 2)
        )