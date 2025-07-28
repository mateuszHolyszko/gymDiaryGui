import pygame
from .Element import Element
from GUI.style import StyleManager, ElementStyle
from dataclasses import asdict
from copy import deepcopy

class Button(Element):
    def __init__(
        self,
        text: str = "",
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 40,
        manager=None,
        parent_panel=None,
        selectable: bool = True,
        neighbors: dict = None,
        font_size: int = 20,
        layer: int = 0,
        style_override: dict = None
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
            layer=layer
        )
        
        self.text = text
        self.font = pygame.font.SysFont("Arial", font_size)
        self.isActive = False

        # Handle style with font separately
        self._base_style = {
            'bg_color': StyleManager.current_style.bg_color,
            'lg_bg_color': StyleManager.current_style.lg_bg_color,
            'text_color': StyleManager.current_style.text_color,
            'border_color': StyleManager.current_style.border_color,
            'highlight_color': StyleManager.current_style.highlight_color,
            'active_bg_color': StyleManager.current_style.active_bg_color
        }
        self._style_overrides = style_override or {}
        self._current_style = self._get_current_style()

    def activate(self):
        self.isActive = True

    def deactivate(self):
        self.isActive = False

    def toggle(self):
        self.isActive = not self.isActive

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
    
    def _get_current_style(self):
        """Returns merged style dictionary with overrides"""
        style = deepcopy(self._base_style)
        style.update(self._style_overrides)
        return style

    @property
    def style(self):
        """Returns style properties as individual attributes"""
        current = self._get_current_style()
        return type('Style', (), current)  # Create simple object with style attributes

    def set_style_override(self, style_dict: dict):
        """Update the button's style overrides"""
        self._style_overrides.update(style_dict)

    def reset_style_override(self):
        """Reset to only using global style"""
        self._style_overrides = {}

    def render(self, screen):
        style = self.style
        
        if self.isActive:
            bg_color = style.active_bg_color
        elif self.is_focused:
            bg_color = style.highlight_color
        else:
            bg_color = style.bg_color
            
        pygame.draw.rect(screen, bg_color, (self.x, self.y, self.width, self.height))
        
        if self.is_focused:
            pygame.draw.rect(screen, style.border_color, 
                           (self.x, self.y, self.width, self.height), 2)

        # If bg_color is not black, font color should be black    
        text_color = style.text_color
        if bg_color != (0,0,0):
            text_color = (0,0,0)

        text = self.font.render(self.text, True, text_color)
        screen.blit(text, (
            self.x + (self.width - text.get_width())//2,
            self.y + (self.height - text.get_height())//2
        ))
