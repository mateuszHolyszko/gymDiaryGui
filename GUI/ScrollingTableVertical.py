import pygame
from GUI.Table import Table
from GUI.elements.Button import Button
from GUI.elements.Label import Label

class ScrollingTableVertical(Table):
    def __init__(self, x, y, width, height, manager, totalHeight, cols=1, cell_height=100):
        super().__init__(x, y, width, height, manager, rows=1, cols=cols)
        self.cell_height = cell_height
        self.totalHeight = totalHeight  # Virtual content height
        self.scroll_offset = 0  # Current scroll offset in pixels
        self.scroll_speed = 25
        self.max_offset = max(0, self.totalHeight - self.height)
        self.enforceElementsSize()


    def handle_event(self, event):
        """Handle events for the panel including scrolling before passing to elements"""
        # First handle scrolling if it's a key event
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_COMMA:  # "<" key
                print("im in")
                self.scroll_offset = max(self.scroll_offset - self.scroll_speed, 0)
                print(self.scroll_offset)
                return True  # Event handled
                
            elif event.key == pygame.K_PERIOD:  # ">" key
                print("im in")
                self.scroll_offset = min(self.scroll_offset + self.scroll_speed, self.max_offset)
                print(self.scroll_offset)
                return True  # Event handled
                
        return False

    def enforceElementsSize(self):
        """Override Table's version to use cell_height and totalHeight."""
        cell_width = self.width / self.cols
        for r in range(len(self.elements_grid)):
            for c in range(self.cols):
                elem = self.elements_grid[r][c]
                if elem:
                    elem.width = cell_width
                    elem.height = self.cell_height
                    elem.x = self.x + c * cell_width
                    elem.y = self.y + r * self.cell_height

    def _reposition_elements(self):
        """Override to skip Table's logic and use our own."""
        self.enforceElementsSize()  # Just use ourversion from ScrollingTable

    def render(self, screen):
        # Create and clear virtual surface
        virtual_surface = pygame.Surface((self.width, self.totalHeight), pygame.SRCALPHA)
        virtual_surface.fill((0, 0, 0, 0))
        
        # Render elements with scroll compensation
        for element in self.getElements():
        # Temporarily adjust coordinates so they're relative to the table's top-left
            original_x, original_y = element.x, element.y
            element.x -= self.x
            element.y -= self.y
            element.render(virtual_surface)
            element.x, element.y = original_x, original_y  # restore absolute positions
        # Create and clear viewport
        # Create viewport and blit visible portion
        viewport = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        viewport.blit(
            virtual_surface,
            (0, 0),  # draw at top-left of viewport
            (0, self.scroll_offset, self.width, self.height)  # grab only the visible region
        )
        
        # Blit visible portion
        viewport.blit(virtual_surface, (self.x, self.y), (self.x, self.y + self.scroll_offset, self.width, self.height))
        
        # Blit to screen
        screen.blit(viewport, (self.x, self.y))

        # ---- Scroll indicator ----
        scroll_bar_x = self.x + self.width + 10  # Just outside the table
        scroll_bar_top = self.y
        scroll_bar_height = self.height
        scroll_bar_width = 4  # Thin line

        # Draw the scroll track
        pygame.draw.rect(screen, (100, 100, 100), (scroll_bar_x, scroll_bar_top, scroll_bar_width, scroll_bar_height))

        # Only show thumb if content overflows
        if self.totalHeight > self.height:
            visible_ratio = self.height / self.totalHeight
            thumb_height = max(20, scroll_bar_height * visible_ratio)  # Ensure visible even for small ratios

            scroll_ratio = self.scroll_offset / (self.totalHeight - self.height)
            thumb_y = scroll_bar_top + scroll_ratio * (scroll_bar_height - thumb_height)

            pygame.draw.rect(screen, (200, 200, 200), (scroll_bar_x, thumb_y, scroll_bar_width, thumb_height))

        # ---- Up/Down scroll indicators ----
        indicator_color = (255, 255, 255)  # white lines & triangles
        line_length = self.width // 5  # make them not full width
        triangle_width = line_length
        triangle_height = 5  # height of the triangle

        # Top indicator (scrolling up possible)
        if self.scroll_offset > 0:
            
            # Triangle pointing upward
            tri_x = self.x + self.width // 2
            tri_y = self.y
            pygame.draw.polygon(screen, indicator_color, [
                (tri_x, tri_y),  # tip
                (tri_x - triangle_width // 2, tri_y + triangle_height),
                (tri_x + triangle_width // 2, tri_y + triangle_height)
            ])
            # Line
            pygame.draw.line(screen, indicator_color,
                             (self.x, tri_y - 2),
                             (self.width, tri_y - 1), 2)

        # Bottom indicator (scrolling down possible)
        if self.scroll_offset < self.max_offset:
            base_y = self.y + self.height - 1
            # Triangle pointing downward
            tri_x = self.x + self.width // 2
            tri_y = base_y - triangle_height
            pygame.draw.polygon(screen, indicator_color, [
                (tri_x, tri_y + triangle_height),  # tip
                (tri_x - triangle_width // 2, tri_y),
                (tri_x + triangle_width // 2, tri_y)
            ])
            # Line
            pygame.draw.line(screen, indicator_color,
                             (self.x, tri_y + triangle_height + 2),
                             (self.width, tri_y + triangle_height + 2), 2)


    def changeDims(self,newTotalHeight):
        self.totalHeight = newTotalHeight
        self.max_offset = max(0, self.totalHeight - self.height)
        self.enforceElementsSize()

    def setNeighbors(self):
        """ Override Set up neighbors, so that if the element is at edge and bellow it or above it there is none, set it to neares one"""
        super().setNeighbors()
        for r in range(self.rows):
            for c in range(self.cols):
                elem = self.elements_grid[r][c]
                if elem is None:
                    continue
                # Up neighbor
                if r > 0 and self.elements_grid[r-1][c] is None:
                    elem.set_neighbor("up", self.getElementsInRow(r-1)[-1])
                # Down neighbor
                if r < self.rows-1 and self.elements_grid[r+1][c] is None:
                     elem.set_neighbor("down", self.getElementsInRow(r+1)[-1])

        


