import pygame
from STL_processor import STLProcessor
from STL_renderer import STLRenderer

def main():
    processor = STLProcessor()
    renderer = STLRenderer()
    
    processor.load_random_stl()
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Rotate model
        processor.rotate_mesh(0.5)
        
        # Render frame
        renderer.clear_buffers()
        if processor.mesh:
            for triangle in processor.mesh.vectors:
                renderer.draw_triangle(triangle)
        renderer.render_frame()
        clock.tick(60)

if __name__ == "__main__":
    main()
    pygame.quit()