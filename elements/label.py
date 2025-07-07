from .base import Element
import pygame

class Label(Element):
    def __init__(self, name, text, x=0, y=0, width=100, height=30, selectable=False):
        super().__init__(name, x, y, width, height, selectable=selectable, text=text)

    def render(self, surface, path, font, x=None, y=None, width=None, height=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        width = self.width if width is None else width
        height = self.height if height is None else height
        is_focused = self is path[-1]
        if self.selectable and is_focused:
            pygame.draw.rect(surface, (80, 80, 80), (x, y, width, height))
        self.render_text(surface, font, x, y, width, height)