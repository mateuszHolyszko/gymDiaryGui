import pygame
from GUI.Panel import Panel

class ScrollingPanelVertical(Panel):
    def __init__(
        self,
        x, y, width, height,
        totalHeight,
        manager,
        padding=0,
    ):
        super().__init__(
            x=x, y=y, width=width, height=height,
            manager=manager,
            layout_type="vertical",
            padding=padding
        )
        self.totalHeight = totalHeight
        self.scroll_offset = 0  # vertical offset (pixels)
        self.scroll_speed = 30  # how much to scroll per key press


    def _get_element_center(self, index):
        """Calculate center position considering scroll offset and totalHeight spacing"""
        spacing = (self.totalHeight - 2 * self.padding) / max(1, len(self.elements))
        center_x = self.x + self.width // 2
        center_y = self.y + self.padding + (index + 0.5) * spacing - self.scroll_offset
        return center_x, center_y

    def _update_element_positions(self):
        """Repositions all elements based on scroll offset"""
        for i, elem in enumerate(self.elements):
            center_x, center_y = self._get_element_center(i)
            elem.position_from_center(center_x, center_y)

    def add_element(self, element):
        """Add element and reposition all based on totalHeight"""
        self.elements.append(element)
        element.parent_panel = self
        self._update_element_positions()

    def render(self, screen):
        """Draw only elements visible within panel window"""
        clip_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        original_clip = screen.get_clip()
        screen.set_clip(clip_rect)  # Limit rendering to panel area

        for element in self.elements:
            if getattr(element, 'parent_panel', None) == self:
                if self._is_visible(element):
                    element.render(screen)

        screen.set_clip(original_clip)  # Restore previous clipping

    def _is_visible(self, element):
        """Return True if any part of the element is within the visible panel area"""
        return (
            element.y + element.height > self.y and
            element.y < self.y + self.height
        )
