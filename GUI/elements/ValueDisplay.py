import pygame
from .Element import Element
from GUI.style import StyleManager
from copy import deepcopy


class ValueDisplay(Element):
    def __init__(
        self,
        prompt: str = "",
        value: str = "",
        arrow_indicator: str = None,  # "up" or "down" or None
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 60,
        manager=None,
        parent_panel=None,
        font_size: int = 16,
        neighbors: dict = None,
        layer: int = 0,
        style_override: dict = None,
        bg_color_prompt: tuple = None  # Optional background color for the prompt area
        
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            manager=manager,
            parent_panel=parent_panel,
            selectable=False,  # Unselectable by default
            neighbors=neighbors,
            layer=layer
        )

        self.prompt = prompt
        self.value = value
        self.arrow_indicator = arrow_indicator  # Optional: "up", "down", or None
        self.font = pygame.font.SysFont("Arial", font_size)
        self.bg_color_prompt = bg_color_prompt

        self._base_style = {
            'bg_color': StyleManager.current_style.bg_color,
            'text_color': StyleManager.current_style.text_color,
            'border_color': StyleManager.current_style.border_color,
        }
        self._style_overrides = style_override or {}
        self._current_style = self._get_current_style()

    def _get_current_style(self):
        style = deepcopy(self._base_style)
        style.update(self._style_overrides)
        return style

    @property
    def style(self):
        current = self._get_current_style()
        return type('Style', (), current)

    def set_value(self, value: str):
        self.value = value

    def set_prompt(self, prompt: str):
        self.prompt = prompt

    def set_arrow(self, direction: str):
        if direction in ("up", "down", None):
            self.arrow_indicator = direction

    def on_press(self):
        # Not selectable, but method defined for compatibility
        pass

    def render(self, screen):
        style = self.style

        # Draw background
        pygame.draw.rect(screen, style.bg_color, (self.x, self.y, self.width, self.height))

        # --- Render prompt (top 1/3) ---
        if self.bg_color_prompt is not None:
            prompt_surface = self.font.render(self.prompt, True, (0,0,0))
        else:
            prompt_surface = self.font.render(self.prompt, True, (255,255,255))
        
        prompt_y = self.y + (self.height // 6) - (prompt_surface.get_height() // 2)
        if self.bg_color_prompt is not None:
            pygame.draw.rect(screen, self.bg_color_prompt, (self.x,self.y,self.width,self.height//3))
        screen.blit(prompt_surface, (
            self.x + (self.width - prompt_surface.get_width()) // 2,
            prompt_y
        )) 

        # --- Draw divider line between prompt and value areas ---
        divider_y = self.y + self.height // 3
        pygame.draw.line(screen, style.border_color, (self.x, divider_y), (self.x + self.width, divider_y), 2)

        # --- Render value (bottom 2/3), supporting multiline ---
        value_lines = self.value.split("\n")
        line_surfaces = [self.font.render(line, True, style.text_color) for line in value_lines]

        # Calculate total height of the lines
        total_text_height = sum(surf.get_height() for surf in line_surfaces)
        value_area_start_y = divider_y
        vertical_padding = (self.height * 2 // 3 - total_text_height) // 2

        current_y = value_area_start_y + vertical_padding
        for surf in line_surfaces:
            screen.blit(surf, (
                self.x + 10,  # Left padding
                current_y
            ))
            current_y += surf.get_height()

        # --- Optional arrow (in value area, right-aligned) ---
        if self.arrow_indicator in ("up", "down"):
            if self.arrow_indicator == "down":
                # Calculate center points
                arrow_offset_x = self.x + self.width - 20
                center_y = self.y + self.height // 2
                
                # Create downward pointing triangle (approximately equilateral)
                arrow_points = [
                    (arrow_offset_x - 10, center_y - 5),  # left point
                    (arrow_offset_x + 10, center_y - 5),  # right point
                    (arrow_offset_x, center_y + 10)       # bottom point
                ]
            else:  # up
                # Calculate center points
                arrow_offset_x = self.x + self.width - 20
                center_y = self.y + self.height // 2
                
                # Create upward pointing triangle (approximately equilateral)
                arrow_points = [
                    (arrow_offset_x - 10, center_y + 5),  # left point
                    (arrow_offset_x + 10, center_y + 5),  # right point
                    (arrow_offset_x, center_y - 10)       # top point
                ]
                
            pygame.draw.polygon(screen, style.text_color, arrow_points)
        # --- Render prompt (top 1/3), supporting multiline ---
        prompt_lines = self.prompt.split("\n")
        line_surfaces = [self.font.render(line, True, style.text_color) for line in prompt_lines]

        # Draw border
        pygame.draw.rect(screen, style.border_color, (self.x, self.y, self.width, self.height), 2)

