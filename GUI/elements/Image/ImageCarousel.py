import random
import time
import pygame
from GUI.elements.Element import Element
from GUI.style import StyleManager
from GUI.elements.Image.Image2D import Image2D

class ImageCarousel(Element):
    def __init__(
        self,
        images: list = None,
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 100,
        manager=None,
        parent_panel=None,
        layer: int = 0,
        mode: str = "random_timed",  # "random_timed", "random_static", "selectable"
        switch_interval: float = 12.0,  # seconds between switches (for random_timed)
        progress_bar_height: int = 5,  # Height of the progress bar in pixels
        progress_bar_color: tuple = (255, 255, 255),  # Color of the progress bar
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
        self.last_switch_time = time.time()  # Initialize with current time
        self.current_index = 0
        self.image_elements = []
        self.progress_bar_height = progress_bar_height
        self.progress_bar_color = progress_bar_color
        
        # Add initial images if provided
        if images:
            for img in images:
                self.add_image(img)
        
        # Shuffle if in random mode
        if "random" in self.mode and self.image_elements:
            random.shuffle(self.image_elements)
    
    def add_image(self, image: Image2D):
        """Add an Image2D instance to the carousel"""
        self._center_image(image)
        self.image_elements.append(image)
        
        if "random" in self.mode:
            random.shuffle(self.image_elements)
    
    def _center_image(self, image: Image2D):
        """Center an image within the carousel's bounds"""
        image.set_position(
            self.x + (self.width - image.width) // 2,
            self.y + (self.height - image.height) // 2
        )
    
    def next_image(self):
        """Switch to next image in sequence"""
        if not self.image_elements:
            return
            
        self.current_index = (self.current_index + 1) % len(self.image_elements)
        self.last_switch_time = time.time()
    
    def random_image(self):
        """Select a random image"""
        if len(self.image_elements) > 1:
            new_index = self.current_index
            while new_index == self.current_index and len(self.image_elements) > 1:
                new_index = random.randint(0, len(self.image_elements)-1)
            self.current_index = new_index
        self.last_switch_time = time.time()
    
    def render(self, screen: pygame.Surface):
        """Draw the current image, progress bar, and handle automatic switching"""
        current_time = time.time()
        
        # Handle automatic switching for timed mode
        if self.mode == "random_timed" and current_time - self.last_switch_time > self.switch_interval:
            self.random_image()
        
        # Draw current image if available
        if self.image_elements:
            self.image_elements[self.current_index].render(screen)
        
        # Draw progress bar for random_timed mode
        if self.mode == "random_timed" and self.image_elements:
            progress = min(1.0, (current_time - self.last_switch_time) / self.switch_interval)
            bar_width = int(self.width * progress)
            
            # Draw background (empty part of progress bar)
            pygame.draw.rect(
                screen, 
                (50, 50, 50),  # Dark gray background
                (self.x, self.y + self.height - self.progress_bar_height, 
                 self.width, self.progress_bar_height)
            )
            
            # Draw progress
            pygame.draw.rect(
                screen, 
                self.progress_bar_color,
                (self.x, self.y + self.height - self.progress_bar_height, 
                 bar_width, self.progress_bar_height)
            )
        
        # Draw border if selectable and focused
        if self.selectable and self.is_focused:
            pygame.draw.rect(
                screen, 
                self.style.highlight_color, 
                (self.x, self.y, self.width, self.height), 
                2
            )
    
    def on_press(self):
        """Handle selection for selectable mode"""
        if self.mode == "selectable":
            self.next_image()
    
    def set_position(self, x: int, y: int):
        """Sets position for carousel and re-centers all images"""
        super().set_position(x, y)
        for img in self.image_elements:
            self._center_image(img)
    
    def update_panel_position(self):
        """Updates position when panel moves (if using offset mode)"""
        super().update_panel_position()
        for img in self.image_elements:
            self._center_image(img)
    
    def set_size(self, width: int, height: int):
        """Update carousel size and re-center all images"""
        self.width = width
        self.height = height
        for img in self.image_elements:
            self._center_image(img)