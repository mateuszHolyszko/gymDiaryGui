import pyglet
from .Element import Element
from GUI.style import StyleManager
from datetime import datetime

class Clock(Element):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 200,
        height: int = 60,
        manager=None,
        parent_panel=None,
        font_size: int = 20,
        layer: int = 0,
        show_date: bool = True,
        show_time: bool = True
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
        self.style = StyleManager.current_style
        self.font_size = font_size
        self.show_date = show_date
        self.show_time = show_time
        self.last_update = 0
        self.current_time = ""
        self.current_date = ""
        self.update_time()

    def update_time(self):
        now = datetime.now()
        if self.show_time:
            self.current_time = now.strftime("%H:%M:%S")
        if self.show_date:
            self.current_date = now.strftime("%d-%m-%Y")

    def render(self, batch):
        # Update time at most once per second
        import time
        current_ticks = int(time.time() * 1000)
        if current_ticks - self.last_update > 1000:
            self.update_time()
            self.last_update = current_ticks

        # Draw background
        pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, color=self.style.bg_color[:3], batch=batch)

        # Prepare text
        texts = []
        if self.show_time:
            texts.append(self.current_time)
        if self.show_date:
            texts.append(self.current_date)

        # Calculate total height
        total_text_height = len(texts) * self.font_size + (len(texts) - 1) * 5 if texts else 0
        current_y = self.y + (self.height - total_text_height) // 2 + self.font_size // 2

        for text in texts:
            label = pyglet.text.Label(
                text,
                font_name='Arial',
                font_size=self.font_size,
                color=self.style.text_color + (255,),
                x=self.x + self.width // 2,
                y=current_y,
                anchor_x='center',
                anchor_y='center',
                batch=batch
            )
            current_y += self.font_size + 5
        batch.draw()

    def on_press(self):
        pass

    def set_position(self, x: int, y: int):
        self._explicit_x = x
        self._explicit_y = y
        if self.parent_panel:
            self.x = self.parent_panel.x + x
            self.y = self.parent_panel.y + y
        else:
            self.x = x
            self.y = y

    def update_panel_position(self):
        if self.parent_panel:
            self.x = self.parent_panel.x + self._explicit_x
            self.y = self.parent_panel.y + self._explicit_y