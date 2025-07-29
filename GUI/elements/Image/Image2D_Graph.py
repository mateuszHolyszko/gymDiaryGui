import pygame
from GUI.elements.Element import Element
from GUI.style import StyleManager

class Image2D_Graph(Element):
    def __init__(
        self,
        image_path: str = None,
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 40,
        manager=None,
        parent_panel=None,
        layer: int = 0,
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            manager=manager,
            parent_panel=parent_panel,
            selectable=False,
            neighbors=None,
            layer=layer
        )
        
        self.style = StyleManager.current_style
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.processed_image = self._process_image(self.original_image)
        self.image = pygame.transform.scale(self.processed_image, (self.width, self.height))
        self.muscleGroups=[] #List of muscle grups displayed on the image, roughly keep the order of how they appear on the image for better readability

    def _get_mapped_color(self, pixel_color):
        """Return the appropriate color based on the exact pixel color."""
        # Define our color mapping with target colors and muscle groups
        color_mapping = {
            (255, 0, 0): "Chest",        # #FF0000
            (255, 52, 0): "Back",         # #FF3400
            (0, 0, 255): "Quads",         # #0000FF
            (52, 52, 255): "Hamstrings",  # #3434FF
            (0, 255, 0): "Biceps",       # #00FF00
            (52, 255, 52): "Triceps",    # #34FF34
            (125, 255, 125): "Shoulders", # #7DFF7D
            (255, 255, 155): "Forearms",  # #FFFF9B
            (255, 125, 55): "Calves",     # #FF7D37
            (125, 52, 255): "Glutes",     # #7D34FF
            (255, 255, 125): "Abs",       # #FFFF7D
        }
        
        # Check for exact color matches
        rgb = (pixel_color.r, pixel_color.g, pixel_color.b)
        if rgb in color_mapping:
            muscle_color = StyleManager.get_muscle_group_color(color_mapping[rgb])["bg_color"]
            return muscle_color
        
        # Keep black pixels as-is (for lines)
        if rgb == (0, 0, 0):
            return (200, 200, 200, 255)
        if rgb == (160,160,160):
            return (160,160,160, 255)    
        # Make everything else transparent
        return (0, 0, 0, 0)

    def _process_image(self, image):
        """Process the image to replace colors according to our exact color mapping."""
        processed_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        
        # Lock the surface for pixel access
        processed_surface.lock()
        image.lock()
        
        for x in range(image.get_width()):
            for y in range(image.get_height()):
                pixel_color = image.get_at((x, y))
                mapped_color = self._get_mapped_color(pixel_color)
                processed_surface.set_at((x, y), mapped_color)
        
        # Unlock the surfaces
        image.unlock()
        processed_surface.unlock()
        
        return processed_surface

    def render(self, screen: pygame.Surface):
        """Draw the image on the screen."""
        screen.blit(self.image, (self.x, self.y))
        
    def on_press(self):
        """Images are not selectable, so this should never be called."""
        pass

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