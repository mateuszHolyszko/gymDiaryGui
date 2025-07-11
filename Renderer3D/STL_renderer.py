import pygame
import numpy as np
from Renderer3D.camera import Camera

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
        self.light_dir = np.array([-1.0, 1.0, 1.0])
        self.light_dir /= np.linalg.norm(self.light_dir)
        self.backface_epsilon = 4e-7

        # Camera setup for "top slightly left" view
        # Model is standardized to roughly [-0.5, 0.5] range.
        camera_position = [-1.0, 1.0, 1.0] # Top, slightly left, and back
        camera_target = [0.0, 0.0, 0.0] # Looking at the origin (center of the standardized model)
        camera_up = [0.0, 1.0, 0.0] # Standard Y-axis up

        # Orthographic projection bounds. These define the viewing volume.
        # Since the model is scaled to 1.0, a range of -1.0 to 1.0 should encompass it.
        ortho_left = -1.0
        ortho_right = 1.0
        ortho_bottom = -1.0
        ortho_top = 1.0
        ortho_near = 0.5 # Near clipping plane
        ortho_far = 5.0 # Far clipping plane

        self.camera = Camera(camera_position, camera_target, camera_up,
                             ortho_left, ortho_right, ortho_bottom, ortho_top, ortho_near, ortho_far)

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
        """Convert 3D point to 2D screen coordinates using camera's view and projection matrices"""
        # Convert point to homogeneous coordinates (add w=1)
        point_h = np.append(point, 1.0)

        # Apply view matrix
        view_matrix = self.camera.get_view_matrix()
        point_view = np.dot(view_matrix, point_h)

        # Apply projection matrix
        proj_matrix = self.camera.get_orthographic_projection_matrix()
        point_clip = np.dot(proj_matrix, point_view)

        # Map from NDC [-1, 1] to screen coordinates [0, width] and [0, height]
        x = int((point_clip[0] + 1) * 0.5 * self.width)
        y = int((1 - (point_clip[1] + 1) * 0.5) * self.height) # Inverted Y for screen coordinates
        
        return x, y, point_clip[2]

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
        
        pygame.draw.polygon(self.surface, color, \
                          [(v0[0], v0[1]), (v1[0], v1[1]), (v2[0], v2[1])])

    def get_surface(self):
        """Get the rendered surface"""
        return self.surface

    def zoom(self, zoom_factor):
        """Passes the zoom request to the camera."""
        self.camera.zoom(zoom_factor)
    def __init__(self, width=200, height=200):
        """Initialize with surface dimensions, not display mode"""
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.depth_buffer = np.full((width, height), np.inf)
        
        # Rendering settings
        self.background = (0, 0, 0)
        self.foreground = (255, 255, 255)
        self.light_dir = np.array([-0.5, 0.5, -0.3])
        self.light_dir /= np.linalg.norm(self.light_dir)
        self.backface_epsilon = 1e-6

        # Camera setup for "top slightly left" view
        # Model is standardized to roughly [-0.5, 0.5] range.
        camera_position = [-1.0, 1.0, 3.0] # Top, slightly left, and back
        camera_target = [0.0, 0.0, 0.0] # Looking at the origin (center of the standardized model)
        camera_up = [0.0, 1.0, 0.0] # Standard Y-axis up

        # Orthographic projection bounds. These define the viewing volume.
        # Since the model is scaled to 1.0, a range of -1.0 to 1.0 should encompass it.
        ortho_left = -1.0
        ortho_right = 1.0
        ortho_bottom = -1.0
        ortho_top = 1.0
        ortho_near = 0.1 # Near clipping plane
        ortho_far = 10.0 # Far clipping plane

        self.camera = Camera(camera_position, camera_target, camera_up,
                             ortho_left, ortho_right, ortho_bottom, ortho_top, ortho_near, ortho_far)

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
        """Convert 3D point to 2D screen coordinates using camera's view and projection matrices"""
        # Convert point to homogeneous coordinates (add w=1)
        point_h = np.append(point, 1.0)

        # Apply view matrix
        view_matrix = self.camera.get_view_matrix()
        point_view = np.dot(view_matrix, point_h)

        # Apply projection matrix
        proj_matrix = self.camera.get_orthographic_projection_matrix()
        point_clip = np.dot(proj_matrix, point_view)

        # Map from NDC [-1, 1] to screen coordinates [0, width] and [0, height]
        x = int((point_clip[0] + 1) * 0.5 * self.width)
        y = int((1 - (point_clip[1] + 1) * 0.5) * self.height) # Inverted Y for screen coordinates
        
        return x, y, point_clip[2]

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
        
        pygame.draw.polygon(self.surface, color, \
                          [(v0[0], v0[1]), (v1[0], v1[1]), (v2[0], v2[1])])

    def get_surface(self):
        """Get the rendered surface"""
        return self.surface