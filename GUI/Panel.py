class Panel:
    def __init__(
        self,
        x, y, width, height,
        manager,
        layout_type="vertical",
        padding=0,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.manager = manager
        self.layout_type = layout_type
        self.padding = padding
        self.elements = []

    def handle_event(self, event):
        """Handle events for all elements in the panel"""
        for element, _ in self.elements:
            if hasattr(element, 'handle_event') and element.handle_event(event):
                return True
        return False

    def getElements(self):
        """Returns a list of elements in the panel."""
        return [e for e in self.elements if e is not None]
    
    def clear_elements(self):
        """Clear all elements from the panel."""
        self.elements = []
    
    def setNeighbors(self):
        """Sets neighbors for all elements based on their layout."""
        elements = self.getElements()
        if self.layout_type == "vertical":
            for i in range(len(elements)):
                if i > 0:
                    elements[i].set_neighbor("up", elements[i-1])
                if i < len(elements) - 1:
                    elements[i].set_neighbor("down", elements[i+1])

        if self.layout_type == "horizontal":
            for i in range(len(elements)):
                if i > 0:
                    elements[i].set_neighbor("left", elements[i-1])
                if i < len(elements) - 1:
                    elements[i].set_neighbor("right", elements[i+1])

    def add_element(self, element):
        """Add element and reposition all based on panel layout"""
        self.elements.append(element)
        element.parent_panel = self

        # Reposition all elements to maintain consistent spacing
        for i, elem in enumerate(self.elements):
            center_x, center_y = self._get_element_center(i)
            elem.position_from_center(center_x, center_y)

    def _get_element_center(self, index):
        """Calculate center position for element at given index"""
        if self.layout_type == "vertical":
            spacing = (self.height - 2*self.padding) / max(1, len(self.elements))
            return (
                self.x + self.width//2,
                self.y + self.padding + (index + 0.5) * spacing
            )
            
        elif self.layout_type == "horizontal":
            spacing = (self.width - 2*self.padding) / max(1, len(self.elements))
            return (
                self.x + self.padding + (index + 0.5) * spacing,
                self.y + self.height//2
            )
            
        elif self.layout_type == "grid":
            cols = 2
            row = index // cols
            col = index % cols
            cell_width = (self.width - 2*self.padding) / cols
            return (
                self.x + self.padding + (col + 0.5) * cell_width,
                self.y + self.padding + (row + 0.5) * cell_width
            )
            
        else:  # free layout
            return (self.x + self.width//2, self.y + self.height//2)

    def render(self, screen):
        # Panel no longer needs to sort elements itself
        for element in self.elements:
            if getattr(element, 'parent_panel', None) == self:
                element.render(screen)
