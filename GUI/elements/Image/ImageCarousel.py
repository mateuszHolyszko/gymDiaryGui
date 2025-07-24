import pygame
import os
import random
import time
from GUI.elements.Element import Element
from GUI.style import StyleManager

class ImageCarousel(Element):
    def __init__(
        self,
        folder_path: str = None,
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 100,
        manager=None,
        parent_panel=None,
        layer: int = 0,
        mode: str = "random_timed",  # "random_timed", "random_static", "selectable"
        switch_interval: float = 3.0,  # seconds between switches (for random_timed)
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            manager=manager,
            parent_panel=parent_panel,
            selectable=(mode == "selectable"),
            neighbors=None,
            layer=layer
        )
        
        self.style = StyleManager.current_style
        self.mode = mode
        self.switch_interval = switch_interval
        self.last_switch_time = 0
        self.current_index = 0
        self.images = []
        self.loaded_images = []
        
        # Load all valid images from folder
        if folder_path and os.path.isdir(folder_path):
            self.folder_path = folder_path
            self.load_images()
        
        # Placeholder if no images loaded
        if not self.images:
            self.images.append(self.create_placeholder())
    
    def load_images(self):
        """Load all valid image files from the folder"""
        valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
        self.images = []
        
        for filename in os.listdir(self.folder_path):
            if any(filename.lower().endswith(ext) for ext in valid_extensions):
                try:
                    img_path = os.path.join(self.folder_path, filename)
                    img = pygame.image.load(img_path).convert_alpha()
                    img = pygame.transform.scale(img, (self.width, self.height))
                    self.images.append(img)
                except Exception as e:
                    print(f"Error loading image {filename}: {e}")
        
        # Shuffle if in random mode
        if "random" in self.mode and self.images:
            random.shuffle(self.images)
    
    def create_placeholder(self):
        """Create a placeholder surface when no images are available"""
        surface = pygame.Surface((self.width, self.height))
        surface.fill(self.style.bg_color)
        pygame.draw.rect(surface, self.style.border_color, (0, 0, self.width, self.height), 2)
        font = pygame.font.SysFont("Arial", 12)
        text = font.render("No Images", True, self.style.text_color)
        surface.blit(text, (
            (self.width - text.get_width()) // 2,
            (self.height - text.get_height()) // 2
        ))
        return surface
    
    def next_image(self):
        """Switch to next image in sequence"""
        if not self.images:
            return
            
        self.current_index = (self.current_index + 1) % len(self.images)
        self.last_switch_time = time.time()
    
    def random_image(self):
        """Select a random image"""
        if len(self.images) > 1:
            new_index = self.current_index
            while new_index == self.current_index and len(self.images) > 1:
                new_index = random.randint(0, len(self.images)-1)
            self.current_index = new_index
        self.last_switch_time = time.time()
    
    def render(self, screen: pygame.Surface):
        """Draw the current image and handle automatic switching"""
        current_time = time.time()
        
        # Handle automatic switching for timed mode
        if self.mode == "random_timed" and current_time - self.last_switch_time > self.switch_interval:
            self.random_image()
        
        # Draw current image
        if self.images:
            screen.blit(self.images[self.current_index], (self.x, self.y))
        
        # Draw border if selectable and focused
        if self.selectable and self.is_focused:
            pygame.draw.rect(screen, self.style.highlight_color, 
                           (self.x, self.y, self.width, self.height), 2)
    
    def on_press(self):
        """Handle selection for selectable mode"""
        if self.mode == "selectable":
            self.next_image()
    
    def reload_images(self):
        """Reload images from folder"""
        self.load_images()
        if not self.images:
            self.images.append(self.create_placeholder())
        self.current_index = 0
    
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