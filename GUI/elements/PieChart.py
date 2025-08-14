import pygame
import math
from .Element import Element
from GUI.style import StyleManager

class PieChart(Element):
    def __init__(
        self,
        distribution: dict,
        x: int = 0,
        y: int = 0,
        width: int = 150+40,
        height: int = 150,
        manager=None,
        parent_panel=None,
        font_size: int = 20,
        layer: int = 0,
        bg_color: tuple = None
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            manager=manager,
            parent_panel=parent_panel,
            selectable=False,  # Charts are always unselectable
            neighbors=None,   # Charts don't participate in navigation
            layer=layer
        )
        self.width = width
        self.height = height
        # Calculate total
        self.font_size = font_size
        self.distribution = distribution
        self.total = sum(self.distribution.values())

        # Center and radius
        #|=======|=======| }\
        #|       | la    |  |
        #|   *   |  be   |   ) height
        #|       |   ls  |  |
        #|=======|=======| }/
        #{height }
        #{     width     }
     
        self.center = (width // 4, height // 2)
        self.radius = height // 2 - 10
        self.colours = self.getColors()

    def getColors(self):
        color_list = []
        for muscle in self.distribution.keys():
            color_info = StyleManager.get_muscle_group_color(muscle)
            color_list.append(color_info['bg_color'])
        return color_list    


    def on_press(self):
        """Charts are not selectable, so this should never be called."""
        pass

    def render(self, screen: pygame.Surface):
        midpoints = []  # List to store (x1, y1) tuples

        # Pass 1: Draw slices and store midpoints
        start_angle = -math.pi / 2
        for i, (label, value) in enumerate(self.distribution.items()):
            slice_angle = (value / self.total) * (2 * math.pi)

            # Draw the slice
            self.draw_pie_slice(
                screen,
                self.colours[i % len(self.colours)],
                self.center,
                self.radius,
                start_angle,
                start_angle + slice_angle
            )

            # Midpoint of the slice
            mid_angle = start_angle + slice_angle / 2
            x1 = self.center[0] + math.cos(mid_angle) * (self.radius / 2)
            y1 = self.center[1] + math.sin(mid_angle) * (self.radius / 2)

            midpoints.append((x1, y1, i))  # Keep track of original slice index

            start_angle += slice_angle

        # Sort midpoints by y-coordinate
        midpoints.sort(key=lambda p: p[1])

        # Pass 2: Draw connecting lines in sorted order
        for sorted_index, (x1, y1, original_i) in enumerate(midpoints):
            x2 = self.height
            y2 = self.height // len(self.distribution) * sorted_index + (self.height // len(self.distribution)) // 2

            # Draw line
            pygame.draw.line(
                screen,
                self.colours[original_i % len(self.colours)],
                (x1, y1),
                (x2, y2),
                4
            )

            # Draw label text
            font = pygame.font.SysFont(None, self.font_size)
            label_text = list(self.distribution.keys())[original_i]
            text_surf = font.render(label_text, True, self.colours[original_i % len(self.colours)])
            screen.blit(text_surf, (x2 + 5, y2 - text_surf.get_height() // 2))



        
    def draw_pie_slice(self,surface, color, center, radius, start_angle, stop_angle, steps=100):
        points = [center]
        for step in range(steps + 1):
            angle = start_angle + (stop_angle - start_angle) * (step / steps)
            x = center[0] + math.cos(angle) * radius
            y = center[1] + math.sin(angle) * radius
            points.append((x, y))
        pygame.draw.polygon(surface, color, points)

    def update(self, newDistribution):
        self.distribution = newDistribution
        self.total = sum(self.distribution.values())
        self.colours = self.getColors()
        