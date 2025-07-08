import pygame
import numpy as np

class STLRenderer:
    def __init__(self, width=200, height=200):
        """Initialize with surface dimensions, not display mode"""
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.depth_buffer = np.full((width, height), np.inf)
        
        # Rendering settings
        self.background = (0, 0, 0)
        self.foreground = (255, 255, 255)
        self.light_dir = np.array([0.5, 0.5, -0.7])
        self.light_dir /= np.linalg.norm(self.light_dir)
        self.backface_epsilon = 1e-6

    def resize(self, new_width, new_height):
        """Handle surface resizing"""
        self.width = new_width
        self.height = new_height
        self.surface = pygame.Surface((new_width, new_height))
        self.depth_buffer = np.full((new_width, new_height), np.inf)

    def clear_buffers(self):
        """Reset surface and depth buffer"""
        self.surface.fill(self.background)
        self.depth_buffer.fill(np.inf)

    def is_backface(self, normal):
        """Backface culling check"""
        return normal[2] <= -self.backface_epsilon

    def calculate_shade(self, normal):
        """Calculate lighting intensity"""
        intensity = np.dot(normal, self.light_dir)
        return max(0.2, intensity)  # Keep ambient light

    def project_point(self, point):
        """Convert 3D point to 2D screen coordinates with depth"""
        x = int((point[0] + 1) * 0.5 * self.width)
        y = int((1 - (point[1] + 1) * 0.5) * self.height)
        return x, y, point[2]  # Include Z for depth

    def draw_triangle(self, triangle, normal):
        """Draw triangle with backface culling and shading"""
        if self.is_backface(normal):
            return
            
        shade = self.calculate_shade(normal)
        color = tuple(int(255 * shade) for _ in range(3))
        
        # Project vertices
        v0 = self.project_point(triangle[0])
        v1 = self.project_point(triangle[1])
        v2 = self.project_point(triangle[2])
        
        # Simple polygon drawing (replace with your preferred method)
        pygame.draw.polygon(self.surface, color, 
                          [(v0[0], v0[1]), (v1[0], v1[1]), (v2[0], v2[1])])

    def get_surface(self):
        """Get the rendered surface"""
        return self.surface