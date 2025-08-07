import pygame
from .Element import Element
from GUI.style import StyleManager

class Label(Element):
    def __init__(
        self,
        text: str = "",
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 40,
        manager=None,
        parent_panel=None,
        font_size: int = 20,
        layer: int = 0,
        text_color: tuple = None,
        bg_color: tuple = None
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            manager=manager,
            parent_panel=parent_panel,
            selectable=False,  # Labels are always unselectable
            neighbors=None,   # Labels don't participate in navigation
            layer=layer
        )
        
        self.text = text
        self.style = StyleManager.current_style
        self.font = pygame.font.SysFont("Arial", font_size)
        
        # Allow custom colors, fall back to style manager defaults
        self._text_color = text_color if text_color else self.style.text_color
        self._bg_color = bg_color if bg_color else self.style.bg_color

    def editText(self, new_text: str):
        """Update the displayed text of the label."""
        self.text = new_text

    def setTextColor(self, color: tuple):
        """Set custom text color (RGB tuple)."""
        self._text_color = color

    def setBackgroundColor(self, color: tuple):
        """Set custom background color (RGB tuple)."""
        self._bg_color = color

    def render(self, screen: pygame.Surface):
        """Draw the label with background and centered text."""
        # Draw background
        pygame.draw.rect(screen, self._bg_color, (self.x, self.y, self.width, self.height))
        
        # Render text
        text_surface = self.font.render(self.text, True, self._text_color)
        
        # Center text in the label
        text_x = self.x + (self.width - text_surface.get_width()) // 2
        text_y = self.y + (self.height - text_surface.get_height()) // 2
        
        screen.blit(text_surface, (text_x, text_y))

    def on_press(self):
        """Labels are not selectable, so this should never be called."""
        pass

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