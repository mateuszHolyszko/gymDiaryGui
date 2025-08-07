import pygame
import pyglet
from .Element import Element
from GUI.style import StyleManager

class InputField(Element):
    def __init__(
        self,
        initial_value: int = 0,
        min_value: int = 0,
        max_value: int = 100,
        step: int = 1,
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 40,
        manager=None,
        parent_panel=None,
        font_size: int = 20,
        layer: int = 0
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            manager=manager,
            parent_panel=parent_panel,
            selectable=True,
            neighbors=None,
            layer=layer
        )
        self.value = initial_value
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.style = StyleManager.current_style
        self.font_size = font_size
        self.is_active = False

    def render(self, batch):
        bg_color = self.style.active_bg_color if self.is_active else (
            self.style.highlight_color if self.is_focused else self.style.bg_color
        )
        pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, color=bg_color[:3], batch=batch)
        if self.is_focused:
            border = pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, color=self.style.border_color[:3], batch=batch)
            border.opacity = 255
        label = pyglet.text.Label(
            str(self.value),
            font_name='Arial',
            font_size=self.font_size,
            color=self.style.text_color + (255,),
            x=self.x + self.width // 2,
            y=self.y + self.height // 2,
            anchor_x='center',
            anchor_y='center',
            batch=batch
        )
        batch.draw()

    def handle_event(self, event) -> bool:
        if not self.is_focused:
            return False
        # Pyglet event: event.type == 'KEYDOWN', event.symbol
        if getattr(event, 'type', None) == 'KEYDOWN':
            from pyglet.window import key
            if event.symbol == key.RETURN:
                self.is_active = not self.is_active
                if not self.is_active:
                    self.on_press()
                return True
            elif self.is_active:
                if event.symbol in (key.LEFT, key.COMMA):
                    self.value = max(self.min_value, self.value - self.step)
                    self.value = round(self.value, 2)
                    return True
                elif event.symbol in (key.RIGHT, key.PERIOD):
                    self.value = min(self.max_value, self.value + self.step)
                    self.value = round(self.value, 2)
                    return True
        return super().handle_event(event)

    def on_press(self):
        """Default press action - can be overridden with lambda."""
        print(f"InputField confirmed value: {self.value}")

    def set_value(self, value: int):
        """Set the value directly, clamped to min/max range."""
        self.value = max(self.min_value, min(self.max_value, value))

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

    def getInput(self, screen, prompt=None):
        """
        Blocking input method: lets user enter a value using <, >, and Enter, without disturbing global focus.
        Returns the entered value (int).
        """
        import pygame
        clock = pygame.time.Clock()
        running = True
        original_value = self.value
        self.is_active = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.is_active = False
                        running = False
                        break
                    elif event.key == pygame.K_ESCAPE:
                        self.value = original_value
                        self.is_active = False
                        running = False
                        break
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_COMMA:
                        self.value = max(self.min_value, self.value - self.step)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_PERIOD:
                        self.value = min(self.max_value, self.value + self.step)
            # Redraw
            screen.fill((0, 0, 0))
            if prompt:
                font = pygame.font.SysFont("Arial", 18)
                prompt_surf = font.render(str(prompt), True, (200, 200, 200))
                screen.blit(prompt_surf, (self.x, self.y - 30))
            self.render(screen)
            pygame.display.flip()
            clock.tick(30)
        return self.value