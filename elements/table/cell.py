from ..base import Element
import pygame

class Cell(Element):
    DATA_TYPES = ["text", "range", "number", "boolean", "select"]  # Available data types
    
    def __init__(self, name, text="", cell_type="cell", selectable=True, on_select=None, on_press=None, data_type="text"):
        super().__init__(name, 0, 0, 0, 0, selectable=selectable, text=text)
        self.cell_type = cell_type.lower()
        self.on_select = on_select
        self.on_press = on_press
        self.padding = 4
        self.row = -1
        self.col = -1
        self.data_type = data_type if data_type in self.DATA_TYPES else "text"
        self._configure_styles()

    def _configure_styles(self):
        if self.cell_type == "header":
            self.background_color = (50, 50, 70)
            self.text_color = (240, 240, 240)
            self.border_color = (90, 90, 110)
            self.selected_color = (80, 80, 130)
        else:
            self.background_color = (40, 40, 40)
            self.text_color = (220, 220, 220)
            self.border_color = (80, 80, 80)
            self.selected_color = (70, 70, 120)
        self.border_thickness = 1

    def set_type(self, cell_type):
        self.cell_type = cell_type.lower()
        self._configure_styles()

    def on_key(self, event):
        if not self.selectable:
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            print(f"{self.cell_type.capitalize()}|Row:'{self.row}'|Col:'{self.col}'|Type:'{self.data_type}'|Text:'{self.text}' pressed!")
            if self.on_press:
                self.on_press()

    def set_data_type(self, data_type):
        """Set the data type if it's valid"""
        if data_type in self.DATA_TYPES:
            self.data_type = data_type
        else:
            print(f"Warning: Invalid data type '{data_type}'. Keeping current type '{self.data_type}'")

    def render(self, surface, path, font, x=None, y=None, width=None, height=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        width = self.width if width is None else width
        height = self.height if height is None else height

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        if not self.selectable:
            fill_color = (30, 30, 30)
            border_color = (60, 60, 60)
            text_color = (120, 120, 120)
        else:
            is_focused = self is path[-1]
            fill_color = self.selected_color if is_focused else self.background_color
            border_color = (100, 100, 255) if is_focused else self.border_color
            text_color = (255, 255, 255) if is_focused else self.text_color

        pygame.draw.rect(surface, fill_color, (x, y, width, height))
        pygame.draw.rect(surface, border_color, (x, y, width, height), self.border_thickness)
        self.render_text(surface, font, x, y, width, height, color=text_color, padding=self.padding)