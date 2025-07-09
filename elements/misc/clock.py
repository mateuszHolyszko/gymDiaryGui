from ..base import Element
import pygame
from datetime import datetime

class Clock(Element):
    def __init__(self, name, x=0, y=0, width=200, height=50, 
                 time_format="%H:%M", date_format="%d-%m-%Y",
                 time_color=(255, 255, 255), date_color=(200, 200, 200),
                 bg_color=(40, 40, 40), selectable=False):
        """
        Clock element that displays current time and date
        
        Args:
            name: Unique identifier for the element
            x, y: Position coordinates
            width, height: Dimensions
            time_format: strftime format for time display (default: "HH:MM")
            date_format: strftime format for date display (default: "YYYY-MM-DD")
            time_color: RGB color for time text
            date_color: RGB color for date text
            bg_color: Background color
            selectable: Whether the clock can receive focus (default: False)
        """
        super().__init__(name, x, y, width, height, selectable=selectable)
        self.time_format = time_format
        self.date_format = date_format
        self.time_color = time_color
        self.date_color = date_color
        self.bg_color = bg_color
        self.last_update = 0  # For tracking when to refresh
        self.current_time = ""
        self.current_date = ""
        
    def update_time(self):
        """Update the current time and date strings"""
        now = datetime.now()
        self.current_time = now.strftime(self.time_format)
        self.current_date = now.strftime(self.date_format)
        
    def render(self, surface, path, font, x=None, y=None, width=None, height=None):
        # Update geometry if parameters are provided
        x = self.x if x is None else x
        y = self.y if y is None else y
        width = self.width if width is None else width
        height = self.height if height is None else height
        
        # Update time if needed (about once per second)
        current_ticks = pygame.time.get_ticks()
        if current_ticks - self.last_update > 1000:  # Update every second
            self.update_time()
            self.last_update = current_ticks
        
        # Draw background
        pygame.draw.rect(surface, self.bg_color, (x, y, width, height))
        
        # Calculate text positions
        time_surface = font.render(self.current_time, True, self.time_color)
        date_surface = font.render(self.current_date, True, self.date_color)
        
        # Center time and date vertically with some spacing
        total_text_height = time_surface.get_height() + date_surface.get_height() + 5
        start_y = y + (height - total_text_height) // 2
        
        # Draw time (centered horizontally)
        time_x = x + (width - time_surface.get_width()) // 2
        surface.blit(time_surface, (time_x, start_y))
        
        # Draw date (centered horizontally)
        date_x = x + (width - date_surface.get_width()) // 2
        surface.blit(date_surface, (date_x, start_y + time_surface.get_height() + 5))