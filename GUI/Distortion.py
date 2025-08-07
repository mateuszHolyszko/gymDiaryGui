import pygame
import numpy as np
import random
import math

class Distortion:
    def __init__(self, width, height, intensity=0.5):
        self.width = width
        self.height = height
        self.intensity = intensity
        self.buffer = pygame.Surface((width, height))
        self.time = 0
        
    def set_intensity(self, intensity):
        """Set the intensity of all effects (0.0 to 1.0)"""
        self.intensity = max(0.0, min(1.0, intensity))
        
    def apply_chromatic_aberration(self, surface):
        """Apply color channel shifting"""
        if self.intensity <= 0:
            return surface
            
        pixels = pygame.surfarray.pixels3d(surface)
        offset = int(2 * self.intensity)
        
        # Shift red and blue channels in opposite directions
        pixels[:,:,0] = np.roll(pixels[:,:,0], offset, axis=1)  # Red channel
        pixels[:,:,2] = np.roll(pixels[:,:,2], -offset, axis=1)  # Blue channel
        
        del pixels  # Unlock the surface
        return surface
    
    def apply_scanlines(self, surface):
        """Add CRT-like scanlines (full width)"""
        if self.intensity <= 0.3:
            return surface
            
        arr = pygame.surfarray.array3d(surface)
        # Darken every other line across full width
        arr[::2,:,:] = (arr[::2,:,:] * (0.9 - (0.1 * self.intensity))).astype(arr.dtype)
        pygame.surfarray.blit_array(surface, arr)
        return surface
    
    def apply_noise(self, surface):
        """Add subtle analog noise"""
        if self.intensity <= 0:
            return surface
            
        pixels = pygame.surfarray.pixels3d(surface)
        noise = np.random.rand(*pixels.shape) * 25 * self.intensity
        pixels[:] = np.clip(pixels + noise, 0, 255)
        del pixels
        return surface
    
    def apply_vhs_glitch(self, surface):
        """Random VHS-style glitch effect"""
        if random.random() < (0.05 * self.intensity):
            pixels = pygame.surfarray.pixels3d(surface)
            glitch_height = random.randint(5, 20)
            glitch_y = random.randint(0, self.height - glitch_height)
            glitch_offset = random.randint(-5, 5) * int(1 + self.intensity * 2)
            
            # Shift a random section horizontally
            glitch_section = pixels[glitch_y:glitch_y+glitch_height,:,:].copy()
            pixels[glitch_y:glitch_y+glitch_height,:,:] = np.roll(glitch_section, glitch_offset, axis=1)
            
            del pixels
        return surface
    
    def apply_sync_jitter(self, surface):
        """Apply digital-style horizontal jitter effect"""
        if self.intensity <= 0:
            return surface

        pixels = pygame.surfarray.pixels3d(surface)

        height, width, _ = pixels.shape

        for y in range(height):
            # Digital jitter: more abrupt and sharp
            jitter_amount = int((random.random() - 0.5) * 3 * self.intensity)

            if y % 3 == 0:  # Stronger jitter on every 3rd row
                jitter_amount += int((random.random() - 0.5) * 5 * self.intensity)

            if abs(jitter_amount) > 1:
                row = pixels[y, :, :]  # shape: (width, 3)
                rolled_row = np.roll(row, jitter_amount, axis=0)
                pixels[y, :, :] = rolled_row.copy()  # Use .copy() to avoid aliasing issues

        # Occasionally add a full-line "pop" effect
        if random.random() < (0.1 * self.intensity):
            shift_y = random.randint(0, height - 1)
            shift_amount = int((random.random() - 0.5) * 20 * self.intensity)
            pop_row = pixels[shift_y, :, :]
            rolled_pop = np.roll(pop_row, shift_amount, axis=0)
            pixels[shift_y, :, :] = rolled_pop.copy()

        del pixels  # Unlock the surface
        return surface

    
    def render(self, surface):
        """Apply all distortion effects with full width coverage"""
        if self.intensity <= 0:
            return
            
        # Ensure we're working with correct dimensions
        if surface.get_size() != (self.width, self.height):
            self.buffer = pygame.Surface(surface.get_size())
            self.width, self.height = surface.get_size()
        
        # Copy to buffer
        self.buffer.blit(surface, (0, 0))
        
        # Apply effects using array3d for full coverage
        self.apply_chromatic_aberration(self.buffer)
        self.apply_scanlines(self.buffer)
        self.apply_noise(self.buffer)
        self.apply_vhs_glitch(self.buffer)
        self.apply_sync_jitter(self.buffer)
        
        # Copy back to original surface
        surface.blit(self.buffer, (0, 0))