import pygame
import numpy as np
from pygame import gfxdraw

class STLRenderer:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.width, self.height = width, height
        
        # Depth buffer (Z-buffer)
        self.depth_buffer = np.full((width, height), np.inf)
        
        # Simple black and white rendering
        self.background = (0, 0, 0)
        self.foreground = (255, 255, 255)
        
        # Lighting setup
        self.light_dir = np.array([0.5, 0.5, -0.7])
        self.light_dir /= np.linalg.norm(self.light_dir)
        
        # Backface culling tolerance
        self.backface_epsilon = 1e-6

    def clear_buffers(self):
        """Reset frame and depth buffers"""
        self.screen.fill(self.background)
        self.depth_buffer.fill(np.inf)

    def is_backface(self, normal):
        """Simple backface culling (now just first pass)"""
        return normal[2] <= -self.backface_epsilon

    def calculate_shade(self, normal):
        """Calculate lighting intensity"""
        intensity = np.dot(normal, self.light_dir)
        return max(0.2, intensity)  # Keep some ambient light

    def project_point(self, point):
        """Convert 3D point to 2D screen coordinates with depth"""
        x = int((point[0] + 1) * 0.5 * self.width)
        y = int((1 - (point[1] + 1) * 0.5) * self.height)
        z = point[2]  # Keep depth value
        return x, y, z

    def draw_triangle(self, triangle):
        """Draw triangle with depth testing"""
        # Project all vertices
        v0 = self.project_point(triangle[0])
        v1 = self.project_point(triangle[1])
        v2 = self.project_point(triangle[2])
        
        # Calculate face normal
        edge1 = triangle[1] - triangle[0]
        edge2 = triangle[2] - triangle[0]
        normal = np.cross(edge1, edge2)
        normal /= np.linalg.norm(normal)
        
        # Backface culling
        if self.is_backface(normal):
            return
            
        # Calculate shading
        shade = self.calculate_shade(normal)
        color = tuple(int(255 * shade) for _ in range(3))
        
        # Get 2D screen coordinates
        points_2d = [(v0[0], v0[1]), (v1[0], v1[1]), (v2[0], v2[1])]
        
        # Get bounding box of triangle
        min_x = max(0, min(v0[0], v1[0], v2[0]))
        max_x = min(self.width-1, max(v0[0], v1[0], v2[0]))
        min_y = max(0, min(v0[1], v1[1], v2[1]))
        max_y = min(self.height-1, max(v0[1], v1[1], v2[1]))
        
        # Skip if outside view
        if min_x >= max_x or min_y >= max_y:
            return
            
        # Precompute barycentric denominator
        denom = (v1[1] - v2[1])*(v0[0] - v2[0]) + (v2[0] - v1[0])*(v0[1] - v2[1])
        if denom == 0:
            return
            
        # Rasterize triangle
        for y in range(min_y, max_y+1):
            for x in range(min_x, max_x+1):
                # Barycentric coordinates
                w0 = ((v1[1]-v2[1])*(x-v2[0]) + (v2[0]-v1[0])*(y-v2[1])) / denom
                w1 = ((v2[1]-v0[1])*(x-v2[0]) + (v0[0]-v2[0])*(y-v2[1])) / denom
                w2 = 1 - w0 - w1
                
                # Check if point is inside triangle
                if w0 >= 0 and w1 >= 0 and w2 >= 0:
                    # Calculate depth (Z value)
                    z = w0*v0[2] + w1*v1[2] + w2*v2[2]
                    
                    # Depth test
                    if z < self.depth_buffer[x, y]:
                        self.depth_buffer[x, y] = z
                        self.screen.set_at((x, y), color)

    def render_frame(self):
        """Complete frame rendering"""
        pygame.display.flip()
        self.clock.tick(60)