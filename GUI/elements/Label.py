import pyglet
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
            selectable=False,
            neighbors=None,
            layer=layer
        )
        self.text = text
        self.style = StyleManager.current_style
        self.font_size = font_size
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

    def render(self, batch):
        # Draw background
        bg = pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, color=self._bg_color[:3], batch=batch)
        # Draw text centered
        label = pyglet.text.Label(
            self.text,
            font_name='Arial',
            font_size=self.font_size,
            color=self._text_color + (255,),
            x=self.x + self.width // 2,
            y=self.y + self.height // 2,
            anchor_x='center',
            anchor_y='center',
            batch=batch
        )
        batch.draw()

    def on_press(self):
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