import pygame
from .Element import Element
from GUI.style import StyleManager

class Button(Element):
    def __init__(
        self,
        text: str = "",
        x: int = 0,  # Absolute or relative to parent
        y: int = 0,
        width: int = 100,
        height: int = 40,
        manager=None,
        parent_panel=None,
        selectable: bool = True,
        neighbors: dict = None,
        font_size: int = 20,
        layer: int = 0  # Now using instance layer
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            manager=manager,
            parent_panel=parent_panel,
            selectable=selectable,
            neighbors=neighbors,
            layer=layer  # Pass layer to Element
        )
        
        # Visual properties
        self.text = text
        self.style = StyleManager.current_style
        self.font = pygame.font.SysFont("Arial", font_size)
        self.isActive = False

    def activate(self):
        self.isActive = True

    def deactivate(self):
        self.isActive = False

    def toggle(self):
        self.isActive = not self.isActive

    def render(self, screen):
        if self.isActive:
            bg_color = self.style.active_bg_color
        elif self.is_focused:
            bg_color = self.style.highlight_color
        else:
            bg_color = self.style.bg_color
        # Draw button background
        pygame.draw.rect(screen, bg_color, (self.x, self.y, self.width, self.height))
        if self.is_focused:
            pygame.draw.rect(screen, self.style.border_color, 
                           (self.x, self.y, self.width, self.height), 2)
        text = self.font.render(self.text, True, self.style.text_color)
        screen.blit(text, (
            self.x + (self.width - text.get_width())//2,
            self.y + (self.height - text.get_height())//2
        ))

    def on_press(self):
        """Default press action - can be overridden with lambda."""
        print(f"Button '{self.text}' pressed!")

    def set_position(self, x: int, y: int):
        """Sets position, treating values as offsets if parent exists."""
        self._explicit_x = x
        self._explicit_y = y
        
        if self.parent_panel:
            self.x = self.parent_panel.x + x
            self.y = self.parent_panel.y + y
        else:
            self.x = x
            self.y = y

    def update_panel_position(self):
        """Updates position when panel moves (if using offset mode)."""
        if self.parent_panel:
            self.x = self.parent_panel.x + self._explicit_x
            self.y = self.parent_panel.y + self._explicit_y