import pygame
from .Element import Element
from GUI.style import StyleManager

class SelectDropDown(Element):
    def __init__(
        self,
        options: list,
        x: int = 0,  # Will be overridden by position_from_center
        y: int = 0,
        width: int = 200,
        height: int = 40,
        manager=None,
        parent_panel=None,
        selectable: bool = True,
        neighbors: dict = None,
        font_size: int = 20,
        layer: int = 0
    ):
        # Initialize with all required Element parameters
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            manager=manager,
            parent_panel=parent_panel,
            selectable=selectable,
            neighbors=neighbors,
            layer=layer
        )
        
        # Dropdown-specific properties
        self.options = options
        self.selected_index = 0
        self.is_expanded = False
        self.font = pygame.font.SysFont("Arial", font_size)
        self.dropdown_height = len(options) * height
        
        # Visual properties
        self.style = StyleManager.current_style
        self.option_rects = []
        self.dropdown_layer = layer + 1  # Dropdown renders above main element
        self._main_center = (0, 0)  # Will be set by position_from_center

    def position_from_center(self, center_x, center_y):
        """Position dropdown relative to center point"""
        super().position_from_center(center_x, center_y)
        self._main_center = (center_x, center_y)  # Store original center

    def render(self, screen):
        """Render dropdown component"""
        # Render main button
        self._render_button(screen)
        
        # Render dropdown if expanded
        if self.is_expanded:
            self._render_dropdown(screen)

    def _render_button(self, screen):
        """Render main button portion"""
        bg_color = self.style.highlight_color if self.is_focused else self.style.bg_color
        text_color = self.style.text_color
        
        # Draw button background
        pygame.draw.rect(screen, bg_color, (self.x, self.y, self.width, self.height))
        
        # Draw selected text (centered)
        selected_text = self.font.render(
            str(self.options[self.selected_index]), 
            True, 
            text_color
        )
        text_x = self.x + (self.width - selected_text.get_width()) // 2
        text_y = self.y + (self.height - selected_text.get_height()) // 2
        screen.blit(selected_text, (text_x, text_y))
        
        # Draw dropdown arrow (right-aligned)
        arrow_points = [
            (self.x + self.width - 20, self.y + self.height // 3),
            (self.x + self.width - 10, self.y + self.height // 3),
            (self.x + self.width - 15, self.y + 2 * self.height // 3)
        ]
        pygame.draw.polygon(screen, text_color, arrow_points)

    def _render_dropdown(self, screen):
        """Render expanded dropdown options"""
        self.option_rects = []
        
        # Create dropdown surface
        dropdown_surface = pygame.Surface((self.width, self.dropdown_height), pygame.SRCALPHA)
        dropdown_surface.fill((*self.style.bg_color, 235))  # Semi-transparent
        
        # Calculate dropdown position (below main button)
        dropdown_x = self.x
        dropdown_y = self.y + self.height
        
        # Render each option
        for i, option in enumerate(self.options):
            option_y = i * self.height
            is_selected = i == self.selected_index
            
            # Option background
            option_color = self.style.highlight_color if is_selected else self.style.bg_color
            pygame.draw.rect(dropdown_surface, option_color, (0, option_y, self.width, self.height))
            
            # Option text (centered)
            option_text = self.font.render(str(option), True, self.style.text_color)
            text_x = (self.width - option_text.get_width()) // 2
            text_y = option_y + (self.height - option_text.get_height()) // 2
            dropdown_surface.blit(option_text, (text_x, text_y))
            
            # Store clickable area
            self.option_rects.append(pygame.Rect(
                dropdown_x, 
                dropdown_y + option_y, 
                self.width, 
                self.height
            ))
        
        # Draw dropdown
        screen.blit(dropdown_surface, (dropdown_x, dropdown_y))
        
        
        

    def on_press(self):
        """Toggle dropdown expansion"""
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            # Lock focus to dropdown while expanded
            self.manager.focus_manager.set_focus(self)
        else:
            # Return focus to previous element
            if hasattr(self, 'previous_focus'):
                self.manager.focus_manager.set_focus(self.previous_focus)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.selectable:
            return False
            
        if self.is_expanded:
            # Handle events for expanded dropdown
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.is_expanded = False
                    return True
                elif event.key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                    return True
                elif event.key == pygame.K_DOWN:
                    self.selected_index = min(len(self.options) - 1, self.selected_index + 1)
                    return True
                elif event.key == pygame.K_ESCAPE:
                    self.is_expanded = False
                    return True
        
        else:
            # Handle events for collapsed dropdown
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.previous_focus = self.manager.focus_manager.current_focus
                self.on_press()
                return True
                
            # Standard element navigation
            return super().handle_event(event)
            
        return False

    def set_neighbor(self, direction: str, element: 'Element'):
        """Override to prevent navigation while expanded"""
        if not self.is_expanded:
            super().set_neighbor(direction, element)

    def getSelectedOption(self) -> str:
        """Get currently selected option"""
        return self.options[self.selected_index] if self.options else None