import pygame
import pyglet
from .Element import Element
from GUI.style import StyleManager
from datetime import datetime, timedelta

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
        self.font_size = font_size
        self.style = StyleManager.current_style
        self.y_label = y_label
        self.x_label = x_label
        self.plotDataColor = self.style.highlight_color
        self.padding = {'left': 50, 'right': 20, 'top': 30, 'bottom': 40}
        self.plot_width = self.width - self.padding['left'] - self.padding['right']
        self.plot_height = self.height - self.padding['top'] - self.padding['bottom']
        self.date_objects = [datetime.strptime(date, '%d-%m-%Y') for date in x_values] if x_values else []
        self._update_date_range()
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

    def render(self, batch):
        style = self.style
        pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, color=style.bg_color[:3], batch=batch)
        plot_x = self.x + self.padding['left']
        plot_y = self.y + self.padding['top']
        if self.y_label:
            pyglet.text.Label(
                self.y_label,
                font_name='Arial',
                font_size=self.font_size,
                color=style.text_color + (255,),
                x=self.x + 5,
                y=self.y + self.height - 20,
                anchor_x='left',
                anchor_y='center',
                batch=batch
            )
        self._draw_axes(batch, plot_x, plot_y)
        if self.x_values and self.y_values and len(self.x_values) == len(self.y_values):
            self._plot_data(batch, plot_x, plot_y)
        self._draw_labels(batch, plot_x, plot_y)
        batch.draw()

    def _draw_axes(self, batch, plot_x, plot_y):
        style = self.style
        # X axis
        pyglet.shapes.Line(
            plot_x, plot_y + self.plot_height,
            plot_x + self.plot_width, plot_y + self.plot_height,
            thickness=2, color=style.text_color[:3], batch=batch
        )
        # Y axis
        pyglet.shapes.Line(
            plot_x, plot_y,
            plot_x, plot_y + self.plot_height,
            thickness=2, color=style.text_color[:3], batch=batch
        )
        # X-axis ticks
        if self.all_dates:
            num_x_ticks = min(5, len(self.all_dates))
            step = max(1, len(self.all_dates) // num_x_ticks)
            for i in range(0, len(self.all_dates), step):
                date = self.all_dates[i]
                days_since_min = (date - self.date_min).days
                total_days = (self.date_max - self.date_min).days
                x_pos = plot_x + int((days_since_min / total_days) * self.plot_width) if total_days > 0 else plot_x
                pyglet.shapes.Line(
                    x_pos, plot_y + self.plot_height,
                    x_pos, plot_y + self.plot_height + 5,
                    thickness=1, color=style.text_color[:3], batch=batch
                )
                date_str = date.strftime('%d-%m')
                pyglet.text.Label(
                    date_str,
                    font_name='Arial',
                    font_size=self.font_size,
                    color=style.text_color + (255,),
                    x=x_pos,
                    y=plot_y + self.plot_height + 12,
                    anchor_x='center',
                    anchor_y='bottom',
                    batch=batch
                )
        # Y-axis ticks
        num_y_ticks = 5
        for i in range(num_y_ticks + 1):
            y = plot_y + self.plot_height - (i * self.plot_height) // num_y_ticks
            pyglet.shapes.Line(
                plot_x - 5, y,
                plot_x, y,
                thickness=1, color=style.text_color[:3], batch=batch
            )
            value = self.y_min + (i * (self.y_max - self.y_min)) / num_y_ticks
            pyglet.text.Label(
                f"{value:.2f}",
                font_name='Arial',
                font_size=self.font_size,
                color=style.text_color + (255,),
                x=plot_x - 8,
                y=y,
                anchor_x='right',
                anchor_y='center',
                batch=batch
            )

    def _format_date_label(self, date_str):
        """Format date string for display (DD-MM)"""
        try:
            day, month, _ = date_str.split('-')
            return f"{day}-{month}"
        except:
            return date_str[:5]  # Fallback to first 5 chars if format is wrong

    def _draw_labels(self, batch, plot_x, plot_y):
        style = self.style
        pyglet.text.Label(
            self.x_label,
            font_name='Arial',
            font_size=self.font_size,
            color=style.text_color + (255,),
            x=plot_x + self.plot_width // 2,
            y=plot_y + self.plot_height + 25,
            anchor_x='center',
            anchor_y='center',
            batch=batch
        )

    def _plot_data(self, batch, plot_x, plot_y):
        style = self.style
        if not self.date_objects or not self.all_dates:
            return
        if self.y_max == self.y_min:
            y_scale = 0.5 * self.plot_height
            y_offset = 0
        else:
            y_scale = self.plot_height / (self.y_max - self.y_min)
            y_offset = self.y_min
        date_to_index = {date: i for i, date in enumerate(self.date_objects)}
        points = []
        for i, date in enumerate(self.date_objects):
            days_since_min = (date - self.date_min).days
            total_days = (self.date_max - self.date_min).days
            x = plot_x + int((days_since_min / total_days) * self.plot_width) if total_days > 0 else plot_x
            y_value = self.y_values[date_to_index[date]]
            y = plot_y + self.plot_height - int((y_value - y_offset) * y_scale)
            points.append((x, y))
        # Draw lines
        if len(points) > 1:
            for i in range(len(points) - 1):
                pyglet.shapes.Line(
                    points[i][0], points[i][1],
                    points[i+1][0], points[i+1][1],
                    thickness=2, color=self.plotDataColor[:3], batch=batch
                )
        # Draw points
        point_radius = 3
        for x, y in points:
            pyglet.shapes.Circle(x, y, point_radius, color=self.plotDataColor[:3], batch=batch)
            pyglet.shapes.Circle(x, y, point_radius-1, color=style.bg_color[:3], batch=batch)

    def handle_event(self, event) -> bool:
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