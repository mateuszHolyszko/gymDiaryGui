import pygame
from .base import Element

class Form(Element):
    def __init__(self, name, prompt="", field_type="text", x=0, y=0, width=400, height=100, on_submit=None):
        super().__init__(name, x, y, width, height, selectable=True)
        self.prompt = prompt
        self.field_type = field_type
        self.on_submit = on_submit
        self._buffer = ""
        self._editing = True
        
        # Visual properties
        self.bg_color = (50, 50, 80)
        self.border_color = (100, 100, 255)
        self.prompt_color = (220, 220, 255)
        self.text_color = (255, 255, 255)

    def on_key(self, event):
        if not self._editing:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.on_submit:
                    self.on_submit(self._buffer)
                return True  # Form will be removed by WindowManager
                
            elif event.key == pygame.K_ESCAPE:
                return True  # Cancel form
                
            elif event.key == pygame.K_BACKSPACE:
                self._buffer = self._buffer[:-1]
            elif self.field_type == "numerical" and event.unicode.isdigit():
                self._buffer += event.unicode
            elif self.field_type == "text" and event.unicode.isprintable():
                self._buffer += event.unicode
                
        return True  # Form consumes all key events

    def render(self, surface, path, font, x=None, y=None, width=None, height=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        width = self.width if width is None else width
        height = self.height if height is None else height
        
        # Draw background and border
        pygame.draw.rect(surface, self.bg_color, (x, y, width, height))
        pygame.draw.rect(surface, self.border_color, (x, y, width, height), 3)
        
        # Draw prompt
        prompt_surf = font.render(self.prompt, True, self.prompt_color)
        surface.blit(prompt_surf, (x + 10, y + 10))
        
        # Draw input text
        text_surf = font.render(self._buffer, True, self.text_color)
        surface.blit(text_surf, (x + 10, y + height//2))
        
        # Draw cursor
        if pygame.time.get_ticks() % 1000 < 500:  # Blinking cursor
            cursor_x = x + 10 + text_surf.get_width()
            pygame.draw.rect(surface, self.text_color, (cursor_x, y + height//2, 2, text_surf.get_height()))