import numpy as np
from stl import mesh
import os
import random

class STLProcessor:
    def __init__(self, models_folder='Renderer3D\models'):
        self.models_folder = models_folder
        self.mesh = None
        self.mesh_name = ""
        
        if not os.path.exists(self.models_folder):
            raise FileNotFoundError(f"Models folder not found")
            
        self.stl_files = [f for f in os.listdir(self.models_folder) 
                         if f.lower().endswith('.stl')]
        
        if not self.stl_files:
            raise FileNotFoundError(f"No STL files found")

    def load_random_stl(self):
        self.mesh_name = random.choice(self.stl_files)
        filepath = os.path.join(self.models_folder, self.mesh_name)
        self.mesh = mesh.Mesh.from_file(filepath)
        self._rotate_mesh_x(-90)  # Fix orientation
        self._standardize_mesh()
        return self.mesh

    def _standardize_mesh(self, target_size=1.0):
        min_coords = np.min(self.mesh.vectors, axis=(0, 1))
        max_coords = np.max(self.mesh.vectors, axis=(0, 1))
        current_size = np.max(max_coords - min_coords)
        
        if current_size > 0:
            center = (min_coords + max_coords) / 2
            self.mesh.vectors -= center
            self.mesh.vectors *= (target_size / current_size)

    def _rotate_mesh_x(self, angle_degrees):
        angle_rad = np.radians(angle_degrees)
        cos, sin = np.cos(angle_rad), np.sin(angle_rad)
        rotation = np.array([
            [1, 0, 0],
            [0, cos, -sin],
            [0, sin, cos]
        ])
        self._apply_rotation(rotation)

    def _apply_rotation(self, rotation):
        for i in range(len(self.mesh.vectors)):
            for j in range(3):
                self.mesh.vectors[i][j] = np.dot(rotation, self.mesh.vectors[i][j])

    def rotate_mesh(self, angle_degrees):
        angle_rad = np.radians(angle_degrees)
        cos, sin = np.cos(angle_rad), np.sin(angle_rad)
        rotation = np.array([
            [cos, 0, sin],
            [0, 1, 0],
            [-sin, 0, cos]
        ])
        self._apply_rotation(rotation)

    def calculate_face_normal(self, triangle):
        v1, v2 = triangle[1] - triangle[0], triangle[2] - triangle[0]
        normal = np.cross(v1, v2)
        norm = np.linalg.norm(normal)
        return normal / norm if norm > 0 else normal