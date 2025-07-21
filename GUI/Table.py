import pygame
from GUI.Panel import Panel
from GUI.elements.Button import Button
from GUI.elements.Label import Label

class Table(Panel):
    def __init__(self, x, y, width, height, manager, rows=1, cols=1, padding=0):
        super().__init__(x, y, width, height, manager, layout_type="grid", padding=padding)
        self.draw_table_lines = True
        self.rows = rows
        self.cols = cols
        # Store elements as a 2D list: rows x cols
        self.elements_grid = [[None for _ in range(cols)] for _ in range(rows)]

    def add_element(self, element, row, col):
        """Add element at specific row, col and reposition all."""
        assert 0 <= row < self.rows and 0 <= col < self.cols, "Row/Col out of bounds"
        self.elements_grid[row][col] = element
        element.parent_panel = self
        self._reposition_elements()

    def getElements(self):
        """Flattened list of all non-None elements."""
        return [e for row in self.elements_grid for e in row if e is not None]
    
    def enforceElementsSize(self):
        """Ensure all elements fit within their grid cells."""
        cell_width = (self.width - 2*self.padding) / self.cols
        cell_height = (self.height - 2*self.padding) / self.rows
        for r in range(self.rows):
            for c in range(self.cols):
                #print(self.elements_grid[r][c])
                if self.elements_grid[r][c] is not None:
                    self.elements_grid[r][c].width = cell_width
                    self.elements_grid[r][c].height = cell_height
                    self.elements_grid[r][c].position_from_center(
                        self.x + self.padding + (c + 0.5) * cell_width,
                        self.y + self.padding + (r + 0.5) * cell_height
                    )
                    

    def setNeighbors(self):
        """Set up neighbors in all four directions for grid layout."""
        for r in range(self.rows):
            for c in range(self.cols):
                elem = self.elements_grid[r][c]
                if elem is None:
                    continue
                # Up neighbor
                if r > 0 and self.elements_grid[r-1][c]:
                    elem.set_neighbor("up", self.elements_grid[r-1][c])
                # Down neighbor
                if r < self.rows-1 and self.elements_grid[r+1][c]:
                    elem.set_neighbor("down", self.elements_grid[r+1][c])
                # Left neighbor
                if c > 0 and self.elements_grid[r][c-1]:
                    elem.set_neighbor("left", self.elements_grid[r][c-1])
                # Right neighbor
                if c < self.cols-1 and self.elements_grid[r][c+1]:
                    elem.set_neighbor("right", self.elements_grid[r][c+1])

    def _get_element_center(self, row, col):
        cell_width = (self.width - 2*self.padding) / self.cols
        cell_height = (self.height - 2*self.padding) / self.rows
        center_x = self.x + self.padding + (col + 0.5) * cell_width
        center_y = self.y + self.padding + (row + 0.5) * cell_height
        return (center_x, center_y)

    def _reposition_elements(self):
        for r in range(self.rows):
            for c in range(self.cols):
                elem = self.elements_grid[r][c]
                if elem is not None:
                    center_x, center_y = self._get_element_center(r, c)
                    elem.position_from_center(center_x, center_y)

    def render(self, screen):
        if self.draw_table_lines == True:
            # Draw table/grid lines
            cell_width = (self.width - 2*self.padding) / self.cols
            cell_height = (self.height - 2*self.padding) / self.rows
            # Vertical lines
            for c in range(self.cols + 1):
                x = int(self.x + self.padding + c * cell_width)
                pygame.draw.line(screen, (180, 180, 180), (x, self.y + self.padding), (x, self.y + self.height - self.padding))
            # Horizontal lines
            for r in range(self.rows + 1):
                y = int(self.y + self.padding + r * cell_height)
                pygame.draw.line(screen, (180, 180, 180), (self.x + self.padding, y), (self.x + self.width - self.padding, y))
        # Render elements
        for elem in self.getElements():
            elem.render(screen)

    def load_data_program(self, data, manager=None, **button_kwargs):
        """
        Populate the table with data (2D list). First row is header (labels), rest are buttons.
        label_class: class to use for header labels
        button_class: class to use for data buttons
        manager: UI manager to pass to elements
        button_kwargs: extra kwargs for button creation
        """
        if not data or not data[0]:
            return
        self.rows = len(data)
        self.cols = len(data[0])
        self.elements_grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        cell_width = (self.width - 2*self.padding) / self.cols
        cell_height = (self.height - 2*self.padding) / self.rows
        for r, row in enumerate(data):
            for c, value in enumerate(row):
                x = self.x + self.padding + c * cell_width
                y = self.y + self.padding + r * cell_height
                if r == 0:
                    elem = Label(
                        text=str(value), x=x, y=y, width=cell_width, height=cell_height, manager=manager, parent_panel=self
                    )
                else:
                    elem = Button(
                        text=str(value), x=x, y=y, width=cell_width, height=cell_height, manager=manager, parent_panel=self, **button_kwargs
                    )
                self.elements_grid[r][c] = elem
        self._reposition_elements()
        self.setNeighbors()
        self.enforceElementsSize()
