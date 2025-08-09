import pygame
from GUI.elements.Element import Element
from GUI.style import StyleManager  # Only if you want styling access, can be removed otherwise

class Image2D(Element):
    def __init__(
        self,
        image_path: str,
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 40,
        manager=None,
        parent_panel=None,
        layer: int = 0
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

        self.style = StyleManager.current_style  # optional, in case styling is used elsewhere
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (self.width, self.height))

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

    def set_image(self, image_path: str):
        """Change the displayed image at runtime."""
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (self.width, self.height))
