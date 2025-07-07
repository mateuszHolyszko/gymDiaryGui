from .base import Element
import pygame

class Panel(Element):
    PADDING = 4  # pixels

    def __init__(self, name, x=0, y=0, width=200, height=200, layout_type="vertical", selectable=True, draw_box=True):
        super().__init__(name, x, y, width, height, selectable=selectable)
        self.layout_type = layout_type  # "vertical" or "horizontal"
        self.draw_box = draw_box

    def render(self, surface, path, font, x=None, y=None, width=None, height=None):
        # Always use panel's own absolute position and size
        x = self.x
        y = self.y
        width = self.width
        height = self.height

        # Only draw box if draw_box is True
        if self.draw_box:
            color = (200, 200, 0) if self in path else (255, 255, 255)
            pygame.draw.rect(surface, color, (x, y, width, height), 2)

        n = len(self.children)
        if n == 0:
            return

        pad = self.PADDING
        if self.layout_type == "vertical":
            slot_height = (height - pad * (n + 1)) // n
            for i, child in enumerate(self.children):
                child_width = getattr(child, "width", width)
                child_height = getattr(child, "height", slot_height)
                # Center child horizontally, center vertically in its slot
                child_x = x + (width - child_width) // 2
                slot_y = y + pad + i * (slot_height + pad)
                child_y = slot_y + (slot_height - child_height) // 2
                child.render(surface, path, font, child_x, child_y, child_width, child_height)
        else:  # horizontal
            slot_width = (width - pad * (n + 1)) // n
            for i, child in enumerate(self.children):
                child_width = getattr(child, "width", slot_width)
                child_height = getattr(child, "height", height)
                # Center child vertically, center horizontally in its slot
                slot_x = x + pad + i * (slot_width + pad)
                child_x = slot_x + (slot_width - child_width) // 2
                child_y = y + (height - child_height) // 2
                child.render(surface, path, font, child_x, child_y, child_width, child_height)

