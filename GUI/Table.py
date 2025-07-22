import pygame
from GUI.Panel import Panel
from GUI.elements.Button import Button
from GUI.elements.Label import Label
from GUI.elements.SessionCell import SessionCell
from workout_db.programs_db import ProgramsDB
from GUI.elements.Element import Element
from GUI.style import StyleManager

class Table(Panel):
    def __init__(self, x, y, width, height, manager, rows=1, cols=1, padding=0):
        super().__init__(x, y, width, height, manager, layout_type="grid", padding=padding)
        self.draw_table_lines = True
        self.rows = rows
        self.cols = cols
        # Store elements as a 2D list: rows x cols
        self.elements_grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.elements = []
        self.database = ProgramsDB()

    def add_element(self, element, row, col):
        """Add element at specific row, col and reposition all."""
        assert 0 <= row < self.rows and 0 <= col < self.cols, "Row/Col out of bounds"
        self.elements_grid[row][col] = element
        if element not in self.elements:  # Keep elements list in sync
            self.elements.append(element)
        element.parent_panel = self
        self._reposition_elements()

    def getElements(self):
        """Flattened list of all non-None elements."""
        return [e for row in self.elements_grid for e in row if e is not None]
    
    def getElementsInRow(self, rowIndex):
        """Returns all non-None elements in the specified row.
        """
        # Handle negative indices (count from end)
        if rowIndex < 0:
            rowIndex = self.rows + rowIndex
        
        if not 0 <= rowIndex < self.rows:
            raise IndexError(f"Row index {rowIndex} out of bounds (valid range: {-self.rows} to {self.rows-1})")
        
        return [elem for elem in self.elements_grid[rowIndex] if elem is not None]
    
    def getSelectable(self, position: int) -> Element:
        """Get the first or last selectable element in the table.
        
        Args:
            position: 1 for first selectable, -1 for last selectable
            
        Returns:
            The first/last selectable Element object or None if none found
        """
        elements = self.getElements()
        
        if not elements:
            return None
            
        if position == 1:  # First selectable
            for elem in elements:
                if getattr(elem, 'selectable', False):
                    return elem
        elif position == -1:  # Last selectable
            for elem in reversed(elements):
                if getattr(elem, 'selectable', False):
                    return elem
                    
        return None
    
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
        # Draw table/grid lines if enabled
        if self.draw_table_lines:
            cell_width = (self.width - 2*self.padding) / self.cols
            cell_height = (self.height - 2*self.padding) / self.rows
            # Vertical lines
            for c in range(self.cols + 1):
                x = int(self.x + self.padding + c * cell_width)
                pygame.draw.line(screen, (180, 180, 180), 
                            (x, self.y + self.padding), 
                            (x, self.y + self.height - self.padding))
            # Horizontal lines
            for r in range(self.rows + 1):
                y = int(self.y + self.padding + r * cell_height)
                pygame.draw.line(screen, (180, 180, 180), 
                            (self.x + self.padding, y), 
                            (self.x + self.width - self.padding, y))
        
        # Render elements sorted by layer
        for element in sorted(self.getElements(), key=lambda e: e.layer):
            element.render(screen)

    def load_data_program(self, data, manager=None, **button_kwargs):
        if not data or not data[0]:
            return
            
        self.rows = len(data)
        self.cols = len(data[0])
        self.elements_grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.elements = []  # Clear existing elements
        
        cell_width = (self.width - 2*self.padding) / self.cols
        cell_height = (self.height - 2*self.padding) / self.rows
        
        for r, row in enumerate(data):
            for c, value in enumerate(row):
                x = self.x + self.padding + c * cell_width
                y = self.y + self.padding + r * cell_height
                if r == 0:
                    elem = Label(
                        text=str(value), x=x, y=y, 
                        width=cell_width, height=cell_height, 
                        manager=manager, parent_panel=self
                    )
                else:
                    elem = Button(
                        text=str(value), x=x, y=y, 
                        width=cell_width, height=cell_height, 
                        manager=manager, parent_panel=self, 
                        **button_kwargs
                    )
                self.elements_grid[r][c] = elem
                self.elements.append(elem)  # Add to elements list for rendering
                
        self._reposition_elements()
        self.setNeighbors()
        self.enforceElementsSize()

    def load_data_session(self, programName, data, manager=None, **button_kwargs):
        if not data:
            # Initialize empty table
            self.rows = 1
            self.cols = 2
            self.elements_grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
            self.elements = []
            return

        # Calculate max number of sets (add 1 extra column for AddSet button)
        set_counts = [len(row) - 1 for row in data if isinstance(row, (list, tuple))]
        max_sets = max(set_counts) if set_counts else 1
        self.rows = len(data)
        self.cols = 1 + max_sets + 1  # 1 for exercise name + max sets columns + 1 for AddSet button
        self.elements_grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.elements = []

        cell_width = (self.width - 2*self.padding) / self.cols
        cell_height = (self.height - 2*self.padding) / self.rows

        for r, row in enumerate(data):
            if not isinstance(row, (list, tuple)) or len(row) == 0:
                continue

            # Exercise name Button
            exercise_name = str(row[0])
            exercise_repRange = self.database.get_repRange(programName, exercise_name)
            exercise_target = self.database.get_target(programName, exercise_name)
            button_elem = Button(
                text=exercise_name,
                x=self.x + self.padding,
                y=self.y + self.padding + r * cell_height,
                width=cell_width,
                height=cell_height,
                manager=manager,
                parent_panel=self
            )
            button_elem.set_style_override({'bg_color': StyleManager.get_muscle_group_color(exercise_target)['bg_color']})
            self.elements_grid[r][0] = button_elem
            self.elements.append(button_elem)

            # Session cells for sets
            for c in range(1, len(row)):
                weight = 0
                reps = 0
                if c < len(row) and isinstance(row[c], (list, tuple)) and len(row[c]) >= 2:
                    weight, reps = row[c][0], row[c][1]

                cell_elem = SessionCell(
                    x=self.x + self.padding + c * cell_width,
                    y=self.y + self.padding + r * cell_height,
                    width=cell_width,
                    height=cell_height,
                    manager=manager,
                    parent_panel=self,
                    weight_previous=weight,
                    reps_previous=reps,
                    rep_range=exercise_repRange,
                    exercise=exercise_name,
                    **button_kwargs
                )
                self.elements_grid[r][c] = cell_elem
                self.elements.append(cell_elem)

            # Add "AddSet" button at the end of each row
            add_set_col = len(row)  # This will be the column after the last set
            add_set_button = Button(
                text="+ Add Set",
                x=self.x + self.padding + add_set_col * cell_width,
                y=self.y + self.padding + r * cell_height,
                width=cell_width,
                height=cell_height,
                manager=manager,
                parent_panel=self
            )
            # Style the button differently
            add_set_button.set_style_override({
                'bg_color': (100, 100, 100),
                'text_color': (255, 255, 255),
                'highlight_color': (150, 150, 150)
            })
            # Add action to the button
            add_set_button.on_press = lambda r=r: self._add_set_to_row(r)
            
            self.elements_grid[r][add_set_col] = add_set_button
            self.elements.append(add_set_button)

        self._reposition_elements()
        self.setNeighbors()
        self.enforceElementsSize()

    def _add_set_to_row(self, row_index):
        """Callback for when AddSet button is pressed"""
        print(f"Adding set to row {row_index}")