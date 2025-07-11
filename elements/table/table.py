from ..base import Element
from .cell import Cell
import pygame

class Table(Element):
    PADDING = 4  # pixels
    
    def __init__(self, name, x=0, y=0, width=200, height=200, cols=1, selectable=True, draw_box=True):
        super().__init__(name, x, y, width, height, selectable=selectable)
        self.cols = cols
        self.rows = 0  # Will be calculated based on data
        self.draw_box = draw_box
        self.cell_padding = 2
        self.layout_type = "table"
        self._data = []  # 2D list to hold row data
        self._column_types = {}
        
    def set_data(self, data):
        """Set table data as a 2D list (list of rows)"""
        self._data = data
        self.rows = len(data)
        self._sync_children()
        
    def add_row(self, row_data):
        """Add a single row of data"""
        self._data.append(row_data)
        self.rows = len(self._data)
        self._sync_children()
        
    def clear_data(self):
        """Clear all table data"""
        self._data = []
        self.rows = 0
        self.children = []

    def set_column_type(self, col_index, data_type):
        """
        Set data type for an entire column
        Args:
            col_index: 0-based column index
            data_type: One of Cell.DATA_TYPES ("text", "range", etc.)
        """
        if data_type in Cell.DATA_TYPES:
            self._column_types[col_index] = data_type
            # Update existing cells in this column
            for cell in self.children:
                if hasattr(cell, 'col') and cell.col == col_index:
                    cell.set_data_type(data_type)
        else:
            print(f"Warning: Invalid data type '{data_type}' for column {col_index}")
        
    def _sync_children(self):
        self.children = []
        for row_idx, row in enumerate(self._data):
            for col_idx, cell_data in enumerate(row[:self.cols]):
                if isinstance(cell_data, Element):
                    cell = cell_data
                    cell.parent = self
                else:
                    # Get column type if specified, default to "text"
                    cell_type = self._column_types.get(col_idx, "text")
                    cell = Cell(
                        f"cell_{row_idx}_{col_idx}", 
                        str(cell_data),
                        data_type=cell_type
                    )
                    cell.parent = self
                
                # Set row and column positions
                if hasattr(cell, 'row'):
                    cell.row = row_idx
                if hasattr(cell, 'col'):
                    cell.col = col_idx
                
                self.children.append(cell)

    def get_cell(self, row, col):
        """Get cell at specified coordinates (0-based indexing)"""
        if not hasattr(self, '_data') or row >= len(self._data) or col >= self.cols:
            return None
            
        # Calculate index in children list
        index = row * self.cols + col
        if index < len(self.children):
            return self.children[index]
        return None
    
    def set_headers(self):
        """Automatically sets first row and first column as headers and makes first row unselectable"""
        if not hasattr(self, '_data') or not self._data:
            return
        
        for row_idx in range(len(self._data)):
            for col_idx in range(min(self.cols, len(self._data[row_idx]))):
                # First row OR first column -> set as header
                if row_idx == 0 or col_idx == 0:
                    cell_idx = row_idx * self.cols + col_idx
                    if cell_idx < len(self.children):
                        cell = self.children[cell_idx]
                        # Only set as header if it's a Cell object
                        if isinstance(cell, Cell):
                            cell.set_type("header")
                            # Make first row completely unselectable
                            if row_idx == 0:
                                cell.selectable = False
        
    def render(self, surface, path, font, x=None, y=None, width=None, height=None):
        x = self.x
        y = self.y
        width = self.width
        height = self.height
        
        if self.draw_box:
            color = (200, 200, 0) if self in path else (255, 255, 255)
            pygame.draw.rect(surface, color, (x, y, width, height), 2)
        
        if not self._data:
            return
            
        # Calculate dynamic height per row if height is not fixed
        pad = self.PADDING
        inner_width = width - 2 * pad
        inner_height = height - 2 * pad
        
        cell_width = (inner_width - (self.cols - 1) * pad) // self.cols
        cell_height = (inner_height - (self.rows - 1) * pad) // self.rows
        
        # Position children in grid cells
        for i, child in enumerate(self.children):
            if i >= self.rows * self.cols:
                break
                
            row = i // self.cols
            col = i % self.cols
            
            cell_x = x + pad + col * (cell_width + pad)
            cell_y = y + pad + row * (cell_height + pad)
            
            child_x = cell_x + self.cell_padding
            child_y = cell_y + self.cell_padding
            child_width = cell_width - 2 * self.cell_padding
            child_height = cell_height - 2 * self.cell_padding
            
            # Update child dimensions if they exist
            if hasattr(child, 'width'):
                child.width = child_width
            if hasattr(child, 'height'):
                child.height = child_height
                
            child.render(surface, path, font, child_x, child_y, child_width, child_height)