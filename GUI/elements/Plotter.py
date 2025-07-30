import pygame
from .Element import Element
from GUI.style import StyleManager

class Plotter(Element):
    def __init__(
        self,
        x_values: list,
        y_values: list,
        x: int = 0,
        y: int = 0,
        width: int = 300,
        height: int = 200,
        manager=None,
        parent_panel=None,
        selectable: bool = False,  # Typically not selectable
        neighbors: dict = None,
        font_size: int = 12,
        layer: int = 0,
        y_label: str = "",
        x_label: str = "X",
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
        
        self.x_values = x_values
        self.y_values = y_values
        self.font = pygame.font.SysFont("Arial", font_size)
        self.style = StyleManager.current_style
        self.y_label = y_label
        self.x_label = x_label
        
        # Calculate padding for axis labels
        self.padding = {
            'left': 40,
            'right': 20,
            'top': 30,
            'bottom': 30
        }
        
        # Calculate plot area dimensions
        self.plot_width = self.width - self.padding['left'] - self.padding['right']
        self.plot_height = self.height - self.padding['top'] - self.padding['bottom']
        
        # Calculate data ranges
        self.x_min = min(x_values) if x_values else 0
        self.x_max = max(x_values) if x_values else 1
        self.y_min = min(y_values) if y_values else 0
        self.y_max = max(y_values) if y_values else 1

    def render(self, screen):
        """Render the plot with axes and data points"""
        # Draw background
        pygame.draw.rect(screen, self.style.bg_color, (self.x, self.y, self.width, self.height))
        
        # Calculate plot area position
        plot_x = self.x + self.padding['left']
        plot_y = self.y + self.padding['top']
        
        # Draw y_label
        if self.y_label:
            title_text = self.font.render(self.y_label, True, self.style.text_color)
            title_x = self.x 
            screen.blit(title_text, (title_x, self.y + 5))
        
        # Plot data points if we have values
        if self.x_values and self.y_values and len(self.x_values) == len(self.y_values):
            self._plot_data(screen, plot_x, plot_y)

        # Draw axes
        self._draw_axes(screen, plot_x, plot_y)
        
        # Draw labels
        self._draw_labels(screen, plot_x, plot_y)
        

    def _draw_axes(self, screen, plot_x, plot_y):
        """Draw the X and Y axes with tick marks"""
        # Draw main axes
        pygame.draw.line(
            screen, self.style.text_color,
            (plot_x, plot_y + self.plot_height),
            (plot_x + self.plot_width, plot_y + self.plot_height),
            2  # X-axis
        )
        pygame.draw.line(
            screen, self.style.text_color,
            (plot_x, plot_y),
            (plot_x, plot_y + self.plot_height),
            2  # Y-axis
        )
        
        # Draw X-axis ticks
        num_x_ticks = min(5, len(self.x_values)) if self.x_values else 5
        for i in range(num_x_ticks + 1):
            x = plot_x + (i * self.plot_width) // num_x_ticks
            pygame.draw.line(
                screen, self.style.text_color,
                (x, plot_y + self.plot_height),
                (x, plot_y + self.plot_height + 5),
                1
            )
            
            # Draw tick label
            if self.x_values:
                value = self.x_min + (i * (self.x_max - self.x_min)) / num_x_ticks
                tick_text = self.font.render(f"{value:.2f}", True, self.style.text_color)
                screen.blit(tick_text, (x - tick_text.get_width() // 2, plot_y + self.plot_height + 7))
        
        # Draw Y-axis ticks
        num_y_ticks = 5
        for i in range(num_y_ticks + 1):
            y = plot_y + self.plot_height - (i * self.plot_height) // num_y_ticks
            pygame.draw.line(
                screen, self.style.text_color,
                (plot_x - 5, y),
                (plot_x, y),
                1
            )
            
            # Draw tick label
            value = self.y_min + (i * (self.y_max - self.y_min)) / num_y_ticks
            tick_text = self.font.render(f"{value:.2f}", True, self.style.text_color)
            screen.blit(tick_text, (plot_x - tick_text.get_width() - 8, y - tick_text.get_height() // 2))

    def _draw_labels(self, screen, plot_x, plot_y):
        """Draw the X and Y axis labels"""
        # X-axis label
        x_label_text = self.font.render(self.x_label, True, self.style.text_color)
        screen.blit(x_label_text,  (plot_x + (self.plot_width - x_label_text.get_width()) // 2,  plot_y + self.plot_height + 25))

    def _plot_data(self, screen, plot_x, plot_y):
        """Plot the actual data points"""
        point_color = self.style.highlight_color
        
        # Plot as connected line
        points = []
        for i in range(len(self.x_values)):
            x = plot_x + int((self.x_values[i] - self.x_min) / (self.x_max - self.x_min) * self.plot_width)
            y = plot_y + self.plot_height - int((self.y_values[i] - self.y_min) / (self.y_max - self.y_min) * self.plot_height)
            points.append((x, y))
        
        # Draw connecting lines
        if len(points) > 1:
            pygame.draw.lines(screen, point_color, False, points, 2)
        
        # Draw points
        point_radius = 3
        for x, y in points:
            pygame.draw.circle(screen, point_color, (x, y), point_radius)
            pygame.draw.circle(screen, self.style.bg_color, (x, y), point_radius - 1)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Plotter typically doesn't handle events as it's not selectable"""
        return False

    def update_data(self, x_values, y_values):
        """Update the plot data and recalculate ranges"""
        self.x_values = x_values
        self.y_values = y_values
        
        if x_values:
            self.x_min = min(x_values)
            self.x_max = max(x_values)
        if y_values:
            self.y_min = min(y_values)
            self.y_max = max(y_values)
        
        # Prevent division by zero if all values are the same
        if self.x_max == self.x_min:
            self.x_max = self.x_min + 1
        if self.y_max == self.y_min:
            self.y_max = self.y_min + 1

    def on_press(self):
        pass