import pygame
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
            selectable=True,  # Input fields are selectable
            neighbors=None,
            layer=layer
        )
        
        self.value = initial_value
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.style = StyleManager.current_style
        self.font = pygame.font.SysFont("Arial", font_size)
        self.is_active = False  # Whether we're actively editing the value

    def render(self, screen: pygame.Surface):
        # Draw background
        bg_color = self.style.active_bg_color if self.is_active else (
            self.style.highlight_color if self.is_focused else self.style.bg_color
        )
        pygame.draw.rect(screen, bg_color, (self.x, self.y, self.width, self.height))
        
        # Draw border if focused
        if self.is_focused:
            pygame.draw.rect(screen, self.style.border_color, 
                          (self.x, self.y, self.width, self.height), 2)
        
        # Render value text
        text = self.font.render(str(self.value), True, self.style.text_color)
        screen.blit(text, (
            self.x + (self.width - text.get_width()) // 2,
            self.y + (self.height - text.get_height()) // 2
        ))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle keyboard events for value adjustment and confirmation."""
        if not self.is_focused:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.is_active = not self.is_active
                if not self.is_active:  # Only trigger on_press when leaving active state
                    self.on_press()
                return True
            
            elif self.is_active:  # Only adjust value when active
                if event.key == pygame.K_LEFT or event.key == pygame.K_COMMA:  # '<' key
                    self.value = max(self.min_value, self.value - self.step)
                    return True
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_PERIOD:  # '>' key
                    self.value = min(self.max_value, self.value + self.step)
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