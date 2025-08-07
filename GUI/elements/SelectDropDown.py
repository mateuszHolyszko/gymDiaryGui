import pygame
import pyglet
from .Element import Element
from GUI.style import StyleManager

class SelectDropDown(Element):
    def __init__(
        self,
        options: list,
        x: int = 0,
        y: int = 0,
        width: int = 200,
        height: int = 40,
        manager=None,
        parent_panel=None,
        selectable: bool = True,
        neighbors: dict = None,
        font_size: int = 20,
        layer: int = 0,
        drop_direction: str = "down"
    ):
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
        self.options = options
        self.selected_index = 0
        self.is_expanded = False
        self.font_size = font_size
        self.dropdown_height = len(options) * height
        self.drop_direction = drop_direction.lower()
        self.style = StyleManager.current_style
        self.option_rects = []
        self.dropdown_layer = layer + 1
        self._main_center = (0, 0)
        if self.drop_direction == "up":
            self.selected_index = len(options) - 1

    def position_from_center(self, center_x, center_y):
        """Position dropdown relative to center point"""
        super().position_from_center(center_x, center_y)
        self._main_center = (center_x, center_y)  # Store original center

    def render(self, batch):
        """Render dropdown component"""
        # Render main button
        self._render_button(batch)
        
        # Render dropdown if expanded
        if self.is_expanded:
            self._render_dropdown(batch)
        batch.draw()

    def _render_button(self, batch):
        bg_color = self.style.highlight_color if self.is_focused else self.style.bg_color
        text_color = self.style.text_color
        pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, color=bg_color[:3], batch=batch)
        label = pyglet.text.Label(
            str(self.options[self.selected_index]) if self.options else "",
            font_name='Arial',
            font_size=self.font_size,
            color=text_color + (255,),
            x=self.x + self.width // 2,
            y=self.y + self.height // 2,
            anchor_x='center',
            anchor_y='center',
            batch=batch
        )
        # Draw dropdown arrow
        arrow_y = self.y + self.height // 2
        if self.drop_direction == "down":
            points = [
                self.x + self.width - 20, arrow_y + 7,
                self.x + self.width - 10, arrow_y + 7,
                self.x + self.width - 15, arrow_y - 7
            ]
        else:
            points = [
                self.x + self.width - 20, arrow_y - 7,
                self.x + self.width - 10, arrow_y - 7,
                self.x + self.width - 15, arrow_y + 7
            ]
        triangle = pyglet.shapes.Triangle(points[0], points[1], points[2], points[3], points[4], points[5], 
                                 color=text_color, batch=batch)
        triangle.draw()

    def _render_dropdown(self, batch):
        self.option_rects = []
        # Dropdown position
        if self.drop_direction == "down":
            dropdown_x = self.x
            dropdown_y = self.y - self.dropdown_height
        else:
            dropdown_x = self.x
            dropdown_y = self.y + self.height
        # Draw dropdown background
        pyglet.shapes.Rectangle(dropdown_x, dropdown_y, self.width, self.dropdown_height, color=self.style.bg_color[:3], batch=batch)
        # Draw options
        for i, option in enumerate(self.options):
            option_y = dropdown_y + i * self.height
            is_selected = i == self.selected_index
            option_color = self.style.highlight_color if is_selected else self.style.bg_color
            pyglet.shapes.Rectangle(dropdown_x, option_y, self.width, self.height, color=option_color[:3], batch=batch)
            label = pyglet.text.Label(
                str(option),
                font_name='Arial',
                font_size=self.font_size,
                color=self.style.text_color + (255,),
                x=dropdown_x + self.width // 2,
                y=option_y + self.height // 2,
                anchor_x='center',
                anchor_y='center',
                batch=batch
            )
            self.option_rects.append((dropdown_x, option_y, self.width, self.height))
        # Draw border
        pyglet.shapes.Rectangle(dropdown_x, dropdown_y, self.width, self.dropdown_height, color=self.style.border_color[:3], batch=batch)

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

    def on_finished_edit(self):
        """Default finished edit action - can be overridden with lambda."""
        print(f"finished editing SelectDropDown with selected option: {self.getSelectedOption()}")

    def handle_event(self, event) -> bool:
        if not self.selectable:
            return False
        from pyglet.window import key
        if self.is_expanded:
            if getattr(event, 'type', None) == 'KEYDOWN':
                if event.symbol == key.RETURN:
                    self.is_expanded = False
                    self.on_finished_edit()
                    return True
                elif event.symbol == key.UP:
                    self.selected_index = max(0, self.selected_index - 1)
                    return True
                elif event.symbol == key.DOWN:
                    self.selected_index = min(len(self.options) - 1, self.selected_index + 1)
                    return True
                elif event.symbol == key.ESCAPE:
                    self.is_expanded = False
                    return True
        else:
            if getattr(event, 'type', None) == 'KEYDOWN' and event.symbol == key.RETURN:
                self.previous_focus = self.manager.focus_manager.current_focus
                self.on_press()
                return True
            return super().handle_event(event)
        return False

    def set_neighbor(self, direction: str, element: 'Element'):
        """Override to prevent navigation while expanded"""
        if not self.is_expanded:
            super().set_neighbor(direction, element)

    def getSelectedOption(self) -> str:
        """Get currently selected option"""
        return self.options[self.selected_index] if self.options else None
    
    def updateOptions(self, new_options: list):
        """Reset index, recalculate dropdown height, and update options"""
        self.options = new_options
        self.selected_index = 0
        self.dropdown_height = len(new_options) * self.height
        if self.drop_direction == "up":
            self.selected_index = len(new_options) - 1
    
    def getInput(self, screen, prompt=None):
        """
        Blocking input method: lets user select an option using arrow keys and Enter.
        Returns the selected option (str) or None if cancelled.
        """
        import pygame
        clock = pygame.time.Clock()
        running = True
        original_index = self.selected_index
        self.is_expanded = True  # Start with dropdown expanded
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.selected_index = original_index
                    break
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.is_expanded = False
                        running = False
                        break
                    elif event.key == pygame.K_ESCAPE:
                        self.selected_index = original_index
                        self.is_expanded = False
                        running = False
                        break
                    elif event.key == pygame.K_UP:
                        self.selected_index = max(0, self.selected_index - 1)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = min(len(self.options) - 1, self.selected_index + 1)
            
            # Redraw
            screen.fill((0, 0, 0))
            
            if prompt:
                font = pygame.font.SysFont("Arial", 18)
                prompt_surf = font.render(str(prompt), True, (200, 200, 200))
                screen.blit(prompt_surf, (self.x,self.y - 30))
            
            # Render the dropdown (both button and expanded options)
            self._render_button(screen)
            self._render_dropdown(screen)
            
            pygame.display.flip()
            clock.tick(30)
        
        return self.getSelectedOption() if self.selected_index != original_index or running else None