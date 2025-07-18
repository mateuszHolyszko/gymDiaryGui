from dataclasses import dataclass
import pygame

@dataclass
class ElementStyle:
    bg_color: tuple
    text_color: tuple
    border_color: tuple
    highlight_color: tuple
    active_bg_color: tuple
    font: pygame.font.Font = None  # Will be initialized later

class StyleManager:
    # Initialize pygame font first
    pygame.font.init()
    
    # Dark theme (white on black)
    DARK = ElementStyle(
        bg_color=(0, 0, 0),          # Black background
        text_color=(255, 255, 255),  # White text
        border_color=(100, 100, 100), # Gray border
        highlight_color=(50, 50, 50), # Dark gray highlight
        active_bg_color=(30, 80, 180), # Blue-ish active background
        font=pygame.font.SysFont("Arial", 20)  # Now initialized properly
    )

    # Light theme (black on white)
    LIGHT = ElementStyle(
        bg_color=(255, 255, 255),
        text_color=(0, 0, 0),
        border_color=(200, 200, 200),
        highlight_color=(220, 220, 220),
        active_bg_color=(100, 160, 255), # Light blue active background
        font=pygame.font.SysFont("Arial", 20)
    )

    current_style = DARK  # Default to dark theme

    @classmethod
    def set_style(cls, style_name: str):
        """Change the active style"""
        cls.current_style = getattr(cls, style_name.upper())