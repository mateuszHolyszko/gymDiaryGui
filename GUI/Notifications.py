import pygame
import time

class Notification:
    def __init__(self, font_size=24, display_time=3.0):
        """
        Notification system that can be called from anywhere
        
        Parameters:
            font_size (int): Font size for notification text
            display_time (float): Default time in seconds to display notifications
        """
        self.font = pygame.font.SysFont("Arial", font_size)
        self.display_time = display_time
        self.current_message = None
        self.start_time = 0
        self.active = False
        self.style = {
            'bg_color': (50, 50, 50),
            'text_color': (255, 255, 255),
            'border_color': (100, 100, 100),
            'padding': 15,
            'border_radius': 5,
            'position': 'top'  # Can be 'top' or 'bottom'
        }

    def show(self, message, display_time=None):
        """
        Display a notification message
        
        Parameters:
            message (str): The message to display
            display_time (float): Optional override of default display time
        """
        self.current_message = message
        self.start_time = time.time()
        self.active = True
        self.display_duration = display_time if display_time is not None else self.display_time

    def render(self, screen):
        """
        Render the notification if active. Call this in your main game loop.
        """
        if not self.active:
            return

        # Calculate remaining display time
        elapsed = time.time() - self.start_time
        if elapsed >= self.display_duration:
            self.active = False
            return

        # Calculate fade effect for both background and text
        progress = elapsed / self.display_duration
        alpha = min(255, int(255 * (1.0 - progress**2)))  # Quadratic fade-out

        # Create notification surface
        text_surface = self.font.render(self.current_message, True, self.style['text_color'])
        
        # Create a surface for the text with per-pixel alpha
        text_alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        text_alpha_surface.blit(text_surface, (0, 0))
        text_alpha_surface.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        
        padding = self.style['padding']
        width = text_surface.get_width() + padding * 2
        height = text_surface.get_height() + padding * 2
        
        # Position at top center of screen
        pos_x = (screen.get_width() - width) // 2
        if self.style['position'] == 'top':
            pos_y = 20  # Offset from top
        else:
            pos_y = screen.get_height() - height - 20  # Original bottom position
        
        # Create background with border and alpha
        background = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(
            background, 
            (*self.style['bg_color'], alpha), 
            (0, 0, width, height),
            border_radius=self.style['border_radius']
        )
        pygame.draw.rect(
            background, 
            (*self.style['border_color'], alpha), 
            (0, 0, width, height),
            width=1,
            border_radius=self.style['border_radius']
        )
        
        # Blit everything to screen
        screen.blit(background, (pos_x, pos_y))
        screen.blit(text_alpha_surface, (pos_x + padding, pos_y + padding))

    def set_position(self, position):
        """Set notification position ('top' or 'bottom')"""
        self.style['position'] = position

    def clear(self):
        """Force clear the current notification"""
        self.active = False
        self.current_message = None