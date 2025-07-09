# File: elements/InputSelect.py
from .base import Element
import pygame

class InputSelect(Element):
    def __init__(self, name, options, x=0, y=0, width=100, height=30, window_manager=None):
        super().__init__(name, x, y, width, height)
        self.options = options
        self.selected_option_index = 0
        self.value = self.options[self.selected_option_index] if self.options else ""
        self._editing = False  # True when options are displayed
        self.window_manager = window_manager
        self.option_height = height  # Height for each option in the dropdown

    def on_key(self, event):
        if not self.selected:
            return False # Return False if not selected, so parent can handle

        if not self._editing:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._editing = True
                print(f"InputSelect '{self.name}' options displayed")
                return True # Event handled: entered editing mode
        else: # _editing is True
            if event.type == pygame.KEYDOWN:
                # Prevent errors if options list is empty when navigating or selecting
                if not self.options:
                    return False # Cannot handle if no options

                if event.key == pygame.K_RETURN:
                    self.value = self.options[self.selected_option_index]
                    self._editing = False
                    print(f"InputSelect '{self.name}' selected value: {self.value}")
                    if self.window_manager:
                        self.window_manager.store_value(self.name, self.value)
                    self.emit("editing_finished", self.value)
                    return True # Event handled: selected option and exited editing
                elif event.key == pygame.K_UP:
                    self.selected_option_index = (self.selected_option_index - 1) % len(self.options)
                    return True # Event handled: navigated up
                elif event.key == pygame.K_DOWN:
                    self.selected_option_index = (self.selected_option_index + 1) % len(self.options)
                    return True # Event handled: navigated down
                elif event.key == pygame.K_u:  # Handle K_u to exit editing mode
                    self._editing = False
                    print(f"InputSelect '{self.name}' options hidden (K_u pressed)")
                    return True # Event handled: exited editing mode
        return False # Event not handled by InputSelect

    def get_display_value(self):
        return self.value

    def render(self, surface, path, font, x=None, y=None, width=None, height=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        width = self.width if width is None else width
        height = self.height if height is None else height

        is_focused = self is path[-1]

        # If _editing is True but the element is no longer focused, exit editing mode
        if self._editing and not is_focused:
            self._editing = False

        border_color = (0, 0, 255) if self in path else (255, 255, 255)
        fill_color = (50, 50, 150) if is_focused else (0, 0, 0)

        # Render the main select field
        pygame.draw.rect(surface, fill_color, (x, y, width, height))
        pygame.draw.rect(surface, border_color, (x, y, width, height), 2)

        display_text = self.get_display_value()
        text_surface = font.render(display_text, True, (255, 255, 255))
        surface.blit(text_surface, (x + 10, y + height // 2 - text_surface.get_height() // 2))

    def renderTop(self, surface, path, font, x=None, y=None, width=None, height=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        width = self.width if width is None else width
        height = self.height if height is None else height

        # Render options if _editing is True
        if self._editing and self.options:
            option_y = y + height
            border_color = (0, 0, 255) # Use the same border color as the main field

            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(x, option_y, width, self.option_height)
                option_fill_color = (70, 70, 170) if i == self.selected_option_index else (30, 30, 130)
                pygame.draw.rect(surface, option_fill_color, option_rect)
                pygame.draw.rect(surface, border_color, option_rect, 1)

                option_text_surface = font.render(option, True, (255, 255, 255))
                surface.blit(option_text_surface, (x + 10, option_y + self.option_height // 2 - option_text_surface.get_height() // 2))
                option_y += self.option_height
