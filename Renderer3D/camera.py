import pygame
import numpy as np

class Camera:
    def __init__(self, position, target, up_vector, ortho_left, ortho_right, ortho_bottom, ortho_top, ortho_near, ortho_far):
        self.position = np.array(position, dtype=np.float32)
        self.target = np.array(target, dtype=np.float32)
        self.up_vector = np.array(up_vector, dtype=np.float32)

        self.ortho_left = ortho_left
        self.ortho_right = ortho_right
        self.ortho_bottom = ortho_bottom
        self.ortho_top = ortho_top
        self.ortho_near = ortho_near
        self.ortho_far = ortho_far

    def get_view_matrix(self):
        # Calculate the camera's local axes
        z_axis = (self.position - self.target) # Camera looks along -Z axis
        z_axis = z_axis / np.linalg.norm(z_axis)

        x_axis = np.cross(self.up_vector, z_axis)
        x_axis = x_axis / np.linalg.norm(x_axis)

        y_axis = np.cross(z_axis, x_axis)

        view_matrix = np.array([
            [x_axis[0], x_axis[1], x_axis[2], -np.dot(x_axis, self.position)],
            [y_axis[0], y_axis[1], y_axis[2], -np.dot(y_axis, self.position)],
            [z_axis[0], z_axis[1], z_axis[2], -np.dot(z_axis, self.position)],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        return view_matrix

    def get_orthographic_projection_matrix(self):
        width = self.ortho_right - self.ortho_left
        height = self.ortho_top - self.ortho_bottom
        depth = self.ortho_far - self.ortho_near

        if width == 0 or height == 0 or depth == 0:
            return np.identity(4, dtype=np.float32)

        proj_matrix = np.array([
            [2 / width, 0, 0, -(self.ortho_right + self.ortho_left) / width],
            [0, 2 / height, 0, -(self.ortho_top + self.ortho_bottom) / height],
            [0, 0, -2 / depth, -(self.ortho_far + self.ortho_near) / depth],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        return proj_matrix

    def zoom(self, zoom_factor):
        """Adjusts the orthographic projection bounds to simulate zoom."""
        if zoom_factor <= 0:
            return

        center_x = (self.ortho_left + self.ortho_right) / 2
        center_y = (self.ortho_bottom + self.ortho_top) / 2

        new_half_width = (self.ortho_right - self.ortho_left) / 2 / zoom_factor
        new_half_height = (self.ortho_top - self.ortho_bottom) / 2 / zoom_factor

        self.ortho_left = center_x - new_half_width
        self.ortho_right = center_x + new_half_width
        self.ortho_bottom = center_y - new_half_height
        self.ortho_top = center_y + new_half_height