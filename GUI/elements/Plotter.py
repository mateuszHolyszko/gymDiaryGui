import pygame
from .Element import Element
from GUI.style import StyleManager
from datetime import datetime, timedelta

class Plotter(Element):
    def __init__(
        self,
        x_values: list,  # List of date strings in format 'DD-MM-YYYY'
        y_values: list,
        x: int = 0,
        y: int = 0,
        width: int = 300,
        height: int = 200,
        manager=None,
        parent_panel=None,
        selectable: bool = False,
        neighbors: dict = None,
        font_size: int = 12,
        layer: int = 0,
        y_label: str = "",
        x_label: str = "Date",
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
        self.plotDataColor = self.style.highlight_color
        
        # Calculate padding for axis labels
        self.padding = {
            'left': 50,  # Increased to accommodate date labels
            'right': 20,
            'top': 30,
            'bottom': 40  # Increased to accommodate rotated date labels
        }
        
        # Calculate plot area dimensions
        self.plot_width = self.width - self.padding['left'] - self.padding['right']
        self.plot_height = self.height - self.padding['top'] - self.padding['bottom']
        
        # Convert date strings to datetime objects for processing
        self.date_objects = [datetime.strptime(date, '%d-%m-%Y') for date in x_values] if x_values else []
        
        # Initialize date range
        self._update_date_range()
        
        # Calculate Y data range
        self._update_y_range()

    def _update_date_range(self):
        """Calculate the full date range from min to max date"""
        if not self.date_objects:
            self.date_min = None
            self.date_max = None
            self.all_dates = []
            return
            
        self.date_min = min(self.date_objects)
        self.date_max = max(self.date_objects)
        
        # Generate all dates in the range
        self.all_dates = []
        current_date = self.date_min
        while current_date <= self.date_max:
            self.all_dates.append(current_date)
            current_date += timedelta(days=1)

    def _update_y_range(self):
        """Calculate the Y-axis range"""
        if not self.y_values:
            self.y_min = 0
            self.y_max = 1
            return
            
        self.y_min = min(self.y_values)*0.9 if self.y_values else 0
        self.y_max = max(self.y_values)*1.1 if self.y_values else 1
        
        # Handle case where all Y values are identical
        if self.y_max == self.y_min:
            if self.y_max == 0:
                self.y_max = 1  # Special case for zero values
            else:
                # Create a small range around the constant value
                self.y_min = self.y_min - abs(self.y_min * 0.1)
                self.y_max = self.y_max + abs(self.y_max * 0.1)

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
        
        # Draw axes first so they appear behind the data
        self._draw_axes(screen, plot_x, plot_y)
        
        # Plot data points if we have values
        if self.x_values and self.y_values and len(self.x_values) == len(self.y_values):
            self._plot_data(screen, plot_x, plot_y)
        
        # Draw labels last so they appear on top
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
        
        # Draw X-axis ticks (date labels)
        if self.all_dates:
            num_x_ticks = min(5, len(self.all_dates))
            step = max(1, len(self.all_dates) // num_x_ticks)
            
            for i in range(0, len(self.all_dates), step):
                date = self.all_dates[i]
                # Calculate X position based on date's position in the full range
                days_since_min = (date - self.date_min).days
                total_days = (self.date_max - self.date_min).days
                x_pos = plot_x + int((days_since_min / total_days) * self.plot_width) if total_days > 0 else plot_x
                
                # Draw tick mark
                pygame.draw.line(
                    screen, self.style.text_color,
                    (x_pos, plot_y + self.plot_height),
                    (x_pos, plot_y + self.plot_height + 5),
                    1
                )
                
                # Draw date label (short format: DD-MM)
                date_str = date.strftime('%d-%m')
                tick_text = self.font.render(date_str, True, self.style.text_color)
                screen.blit(tick_text, (x_pos - tick_text.get_width() // 2, plot_y + self.plot_height + 7))
        
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

    def _format_date_label(self, date_str):
        """Format date string for display (DD-MM)"""
        try:
            day, month, _ = date_str.split('-')
            return f"{day}-{month}"
        except:
            return date_str[:5]  # Fallback to first 5 chars if format is wrong

    def _draw_labels(self, screen, plot_x, plot_y):
        """Draw the X and Y axis labels"""
        # X-axis label
        x_label_text = self.font.render(self.x_label, True, self.style.text_color)
        screen.blit(x_label_text, (plot_x + (self.plot_width - x_label_text.get_width()) // 2, plot_y + self.plot_height + 25))

    def _plot_data(self, screen, plot_x, plot_y):
        """Plot the actual data points"""
        if not self.date_objects or not self.all_dates:
            return
            
        # Calculate Y scaling factor
        if self.y_max == self.y_min:
            y_scale = 0.5 * self.plot_height
            y_offset = 0
        else:
            y_scale = self.plot_height / (self.y_max - self.y_min)
            y_offset = self.y_min
        
        # Create a mapping from dates to their indices in the original data
        date_to_index = {date: i for i, date in enumerate(self.date_objects)}
        
        # Plot as connected line
        points = []
        for i, date in enumerate(self.date_objects):
            # Calculate X position based on date's position in the full range
            days_since_min = (date - self.date_min).days
            total_days = (self.date_max - self.date_min).days
            x = plot_x + int((days_since_min / total_days) * self.plot_width) if total_days > 0 else plot_x
            
            # Get the corresponding Y value
            y_value = self.y_values[date_to_index[date]]
            y = plot_y + self.plot_height - int((y_value - y_offset) * y_scale)
            points.append((x, y))
        
        # Draw connecting lines
        if len(points) > 1:
            pygame.draw.lines(screen, self.plotDataColor, False, points, 2)
        
        # Draw points
        point_radius = 3
        for x, y in points:
            pygame.draw.circle(screen, self.plotDataColor, (x, y), point_radius)
            pygame.draw.circle(screen, self.style.bg_color, (x, y), point_radius - 1)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Plotter typically doesn't handle events as it's not selectable"""
        return False

    def update_data(self, x_values, y_values):
        """Update the plot data and recalculate ranges"""
        self.x_values = x_values
        self.y_values = y_values
        self.date_objects = [datetime.strptime(date, '%d-%m-%Y') for date in x_values] if x_values else []
        
        # Update date range
        self._update_date_range()
        self._update_y_range()
    def on_press(self):
        pass

    def change_plot_color(self, color):
        self.plotDataColor = color