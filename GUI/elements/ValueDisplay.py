import pygame
import pyglet
from .Element import Element
from GUI.style import StyleManager
from copy import deepcopy

class ValueDisplay(Element):
    def __init__(
        self,
        prompt: str = "",
        value: str = "",
        arrow_indicator: str = None,
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
        bg_color_prompt: tuple = None
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            manager=manager,
            parent_panel=parent_panel,
            selectable=False,
            neighbors=neighbors,
            layer=layer
        )
        self.prompt = prompt
        self.value = value
        self.arrow_indicator = arrow_indicator
        self.font_size = font_size
        self.bg_color_prompt = bg_color_prompt
        self._base_style = {
            'bg_color': StyleManager.current_style.bg_color,
            'text_color': StyleManager.current_style.text_color,
            'border_color': StyleManager.current_style.border_color,
        }
        self._style_overrides = style_override or {}

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

    def render(self, batch):
        style = self.style
        # Background
        pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, color=style.bg_color[:3], batch=batch)
        # Prompt area
        if self.bg_color_prompt is not None:
            pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height//3, color=self.bg_color_prompt[:3], batch=batch)
        prompt_label = pyglet.text.Label(
            self.prompt,
            font_name='Arial',
            font_size=self.font_size,
            color=(0,0,0,255) if self.bg_color_prompt else (255,255,255,255),
            x=self.x + self.width // 2,
            y=self.y + self.height // 6,
            anchor_x='center',
            anchor_y='center',
            batch=batch
        )
        # Divider
        divider_y = self.y + self.height // 3
        pyglet.shapes.Line(self.x, divider_y, self.x + self.width, divider_y, thickness=2, color=style.border_color[:3], batch=batch)
        # Value area (multiline)
        value_lines = self.value.split("\n")
        for i, line in enumerate(value_lines):
            label = pyglet.text.Label(
                line,
                font_name='Arial',
                font_size=self.font_size,
                color=style.text_color + (255,),
                x=self.x + 10,
                y=divider_y + (self.height * 2 // 3) - (i+1)*self.font_size - 5,
                anchor_x='left',
                anchor_y='baseline',
                batch=batch
            )
        # Arrow indicator (draw as triangle)
        if self.arrow_indicator in ("up", "down"):
            arrow_offset_x = self.x + self.width - 20
            center_y = self.y + self.height // 2
            if self.arrow_indicator == "down":
                points = [arrow_offset_x - 10, center_y - 5, arrow_offset_x + 10, center_y - 5, arrow_offset_x, center_y + 10]
            else:
                points = [arrow_offset_x - 10, center_y + 5, arrow_offset_x + 10, center_y + 5, arrow_offset_x, center_y - 10]
            pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES, ('v2i', points), ('c3B', style.text_color[:3]*3))
        # Border
        pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, color=style.border_color[:3], batch=batch)
        batch.draw()
