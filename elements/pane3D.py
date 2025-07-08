from .base import Element
from Renderer3D.STL_processor import STLProcessor
from Renderer3D.STL_renderer import STLRenderer
import pygame
import os

class Pane3D(Element):
    def __init__(self, name, stl_file, x=0, y=0, width=200, height=200, selectable=True):
        super().__init__(name, x, y, width, height, selectable)
        self.stl_file = stl_file
        self.rotation_speed = 0.5
        self.processor = STLProcessor()
        self.renderer = STLRenderer(width, height)
        self._initialize_rendering()

    def _initialize_rendering(self):
        """Initialize the STL processor"""
        try:
            self.processor.models_folder = os.path.dirname(self.stl_file)
            self.processor.stl_files = [os.path.basename(self.stl_file)]
            self.processor.load_random_stl()
        except Exception as e:
            print(f"Error initializing 3D pane: {e}")
            self.processor.mesh = None

    def render(self, surface, path, font, x=None, y=None, width=None, height=None):
        """
        Render the 3D model following GUI conventions
        """
        # Use provided coordinates if available, otherwise use element's own
        render_x = self.x if x is None else x
        render_y = self.y if y is None else y
        render_width = self.width if width is None else width
        render_height = self.height if height is None else height

        # Handle failed initialization
        if self.processor.mesh is None:
            pygame.draw.rect(surface, (100, 100, 100), (render_x, render_y, render_width, render_height))
            text = font.render("3D View", True, (255, 255, 255))
            surface.blit(text, (render_x + render_width//2 - text.get_width()//2, 
                             render_y + render_height//2 - text.get_height()//2))
            return

        # Resize renderer if dimensions changed
        if (self.renderer.width != render_width or 
            self.renderer.height != render_height):
            self.renderer.resize(render_width, render_height)

        # Rotate model continuously
        self.processor.rotate_mesh(self.rotation_speed)

        # Prepare and execute rendering
        self.renderer.clear_buffers()
        for triangle in self.processor.mesh.vectors:
            normal = self.processor.calculate_face_normal(triangle)
            self.renderer.draw_triangle(triangle, normal)

        # Draw selection border if focused
        if self in path:
            pygame.draw.rect(self.renderer.surface, (255, 255, 255), 
                           (0, 0, render_width, render_height), 2)

        # Blit the rendered content to parent surface
        surface.blit(self.renderer.get_surface(), (render_x, render_y))

    def on_key(self, event):
        """Handle keyboard input for rotation control"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.rotation_speed -= 0.1
                return True
            elif event.key == pygame.K_RIGHT:
                self.rotation_speed += 0.1
                return True
            elif event.key == pygame.K_UP:
                self.rotation_speed = 0
                return True
        return False