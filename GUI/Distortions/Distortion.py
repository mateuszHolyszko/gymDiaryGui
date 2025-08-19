import pygame
import os
from pygame_shaders import Shader

class Distortion:
    def __init__(self, width, height, intensity=0.5):
        self.width = width
        self.height = height
        self.intensity = intensity
        
        # Create two surfaces - one for pre-shader content, one for post-shader
        self.pre_shader_surface = pygame.Surface((width, height))
        self.post_shader_surface = pygame.Surface((width, height))
        
        # Load shaders
        base_dir = os.path.dirname(os.path.abspath(__file__))
        vert_path = os.path.join(base_dir, "distortion.vert")
        frag_path = os.path.join(base_dir, "distortion.frag")
        #print(vert_path)
        
        try:
            # Initialize shader with the POST-shader surface as target
            self.shader = Shader(
                vertex_path=vert_path,
                fragment_path=frag_path,
                target_surface=self.post_shader_surface
            )
        except Exception as e:
            print(f"Shader initialization failed: {e}")
            self.shader = None
    
    def render(self, surface):
        if not self.shader:
            return
            
        # 1. Capture current screen content
        self.pre_shader_surface.blit(surface, (0, 0))
        
        # 2. Process through shader
        self.post_shader_surface.blit(self.pre_shader_surface, (0, 0))
        self.shader.render()  # Applies shader to post_shader_surface
        
        # 3. Copy back to original surface
        surface.blit(self.post_shader_surface, (0, 0))