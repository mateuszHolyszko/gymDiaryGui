from .base import Element
import pygame

class InputField(Element):
    def __init__(self, name, x=0, y=0, width=100, height=30, field_type="text", window_manager=None):
        super().__init__(name, x, y, width, height)
        self.field_type = field_type  # "text" or "numerical"
        self.value = ""
        self._editing = False
        self._buffer = ""
        self.window_manager = window_manager

    def on_key(self, event):
        if not self.selected:
            return

        if not self._editing:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._editing = True
                self._buffer = ""
                print(f"InputField '{self.name}' editing started (type: {self.field_type})")
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.value = self._buffer
                    self._editing = False
                    print(f"InputField '{self.name}' saved value: {self.value}")
                    if self.window_manager:
                        self.window_manager.store_value(self.name, self.value)
                    self.emit("editing_finished", self.value)  # <-- emit signal here
                elif event.key == pygame.K_u:
                    self._editing = False
                    print(f"InputField '{self.name}' input discarded")
                elif event.key == pygame.K_BACKSPACE:
                    self._buffer = self._buffer[:-1]
                else:
                    char = event.unicode
                    if self.field_type == "numerical":
                        if char.isdigit():
                            self._buffer += char
                    else:
                        if char.isprintable():
                            self._buffer += char

    def get_display_value(self):
        if self._editing:
            return self._buffer
        return self.value
    
    def render(self, surface, path, font, x=None, y=None, width=None, height=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        width = self.width if width is None else width
        height = self.height if height is None else height
        is_focused = self is path[-1]
        border_color = (0, 0, 255) if self in path else (255, 255, 255)
        fill_color = (50, 50, 150) if is_focused else (0, 0, 0)
        pygame.draw.rect(surface, fill_color, (x, y, width, height))
        pygame.draw.rect(surface, border_color, (x, y, width, height), 2)
        value = self.get_display_value()
        text_surface = font.render(value, True, (255, 255, 255))
        surface.blit(text_surface, (x + 10, y + height // 2 - text_surface.get_height() // 2))