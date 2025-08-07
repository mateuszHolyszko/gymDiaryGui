import pygame
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
            selectable=False,  # Clock is not selectable
            neighbors=None,   # Doesn't participate in navigation
            layer=layer
        )
        
        self.style = StyleManager.current_style
        self.font = pygame.font.SysFont("Arial", font_size)
        self.show_date = show_date
        self.show_time = show_time
        self.last_update = 0
        self.current_time = ""
        self.current_date = ""

    def update_time(self):
        """Update the time and date strings"""
        now = datetime.now()
        if self.show_time:
            self.current_time = now.strftime("%H:%M:%S")
        if self.show_date:
            self.current_date = now.strftime("%d-%m-%Y")

    def render(self, screen: pygame.Surface):
        """Draw the clock with current time and date"""
        # Update time at most once per second
        current_ticks = pygame.time.get_ticks()
        if current_ticks - self.last_update > 1000:  # Update every second
            self.update_time()
            self.last_update = current_ticks
        
        # Draw background
        pygame.draw.rect(screen, self.style.bg_color, (self.x, self.y, self.width, self.height))
        
        # Prepare text surfaces
        texts = []
        if self.show_time:
            time_surface = self.font.render(self.current_time, True, self.style.text_color)
            texts.append(time_surface)
        if self.show_date:
            date_surface = self.font.render(self.current_date, True, self.style.text_color)
            texts.append(date_surface)
        
        # Calculate total height of all text elements
        total_text_height = sum(text.get_height() for text in texts)
        if len(texts) > 1:
            total_text_height += (len(texts) - 1) * 5  # Add 5px spacing between lines
        
        # Draw each text element centered
        current_y = self.y + (self.height - total_text_height) // 2
        for text_surface in texts:
            text_x = self.x + (self.width - text_surface.get_width()) // 2
            screen.blit(text_surface, (text_x, current_y))
            current_y += text_surface.get_height() + 5  # Move down for next line

    def on_press(self):
        """Clock is not selectable, so this should never be called"""
        pass

    def set_position(self, x: int, y: int):
        """Sets position, treating values as offsets if parent exists"""
        self._explicit_x = x
        self._explicit_y = y
        
        if self.parent_panel:
            self.x = self.parent_panel.x + x
            self.y = self.parent_panel.y + y
        else:
            self.x = x
            self.y = y

    def update_panel_position(self):
        """Updates position when panel moves (if using offset mode)"""
        if self.parent_panel:
            self.x = self.parent_panel.x + self._explicit_x
            self.y = self.parent_panel.y + self._explicit_y