from dataclasses import dataclass
import pygame

@dataclass
class ElementStyle:
    bg_color: tuple
    lg_bg_color: tuple
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
        bg_color=(0, 0, 0),
        lg_bg_color=(25, 25, 25),
        text_color=(255, 255, 255),
        border_color=(100, 100, 100),
        highlight_color=(50, 50, 50),
        active_bg_color=(30, 80, 180),
        font=pygame.font.SysFont("Arial", 20)
    )

    # Light theme (black on white)
    LIGHT = ElementStyle(
        bg_color=(255, 255, 255),
        lg_bg_color=(230, 230, 230),
        text_color=(0, 0, 0),
        border_color=(200, 200, 200),
        highlight_color=(220, 220, 220),
        active_bg_color=(100, 160, 255),
        font=pygame.font.SysFont("Arial", 20)
    )

    current_style = DARK  # Default to dark theme

    @classmethod
    def set_style(cls, style_name: str):
        """Change the active style"""
        cls.current_style = getattr(cls, style_name.upper())

    @classmethod
    def get_muscle_group_color(cls, muscle_group: str) -> dict:
        """
        Given a muscle group name, return its background and text color.
        """
        muscle_groups = [
            "Chest", "Back", "Quads", "Hamstrings", "Shoulders", "Biceps",
            "Triceps", "Abs", "Calves", "Glutes", "Forearms"
        ]

        color_palette = [
            (220, 20, 60),    # Crimson
            (0, 128, 128),    # Teal
            (255, 140, 0),    # Dark Orange
            (75, 0, 130),     # Indigo
            (34, 139, 34),    # Forest Green
            (255, 105, 180),  # Hot Pink
            (70, 130, 180),   # Steel Blue
            (255, 215, 0),    # Gold
            (138, 43, 226),   # Blue Violet
            (0, 191, 255),    # Deep Sky Blue
            (205, 92, 92)     # Indian Red
        ]

        # Normalize input to match format
        muscle_group = muscle_group.strip().capitalize()

        if muscle_group not in muscle_groups:
            raise ValueError(f"Unknown muscle group: {muscle_group}")

        index = muscle_groups.index(muscle_group)
        bg_color = color_palette[index % len(color_palette)]

        return {
            "bg_color": bg_color,
            "text_color": cls.current_style.text_color
        }
    
    def desaturate_color(rgb_tuple, saturation_factor=0.7):
        """Reduce color saturation by converting to HSL and back"""
        import colorsys
        # Convert RGB to HSL (colorsys uses 0-1 range)
        r, g, b = [x/255 for x in rgb_tuple]
        h, s, l = colorsys.rgb_to_hls(r, g, b)
        # Reduce saturation
        s = max(0, min(1, s * saturation_factor))
        # Convert back to RGB
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (int(r*255), int(g*255), int(b*255))
    
    def gray_out_color(rgb_tuple, gray_factor=0.5):
        """
        Gray out a color by mixing it with gray at the same brightness level
        Args:
            rgb_tuple: (r, g, b) color tuple (0-255)
            gray_factor: 0.0 = original color, 1.0 = fully gray
        Returns:
            (r, g, b) desaturated color tuple
        """
        r, g, b = rgb_tuple
        
        # Calculate brightness (luminance)
        brightness = 0.299 * r + 0.587 * g + 0.114 * b
        
        # Mix with gray at same brightness
        new_r = int(r * (1 - gray_factor) + brightness * gray_factor)
        new_g = int(g * (1 - gray_factor) + brightness * gray_factor)
        new_b = int(b * (1 - gray_factor) + brightness * gray_factor)
        
        return (new_r, new_g, new_b)
