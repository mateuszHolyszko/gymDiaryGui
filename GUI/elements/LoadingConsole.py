import pygame
import random
from .Element import Element
from GUI.style import StyleManager


class LoadingConsole(Element):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 40,
        manager=None,
        parent_panel=None,
        font_size: int = 20,
        layer: int = 0,
        text_color: tuple = None,
        bg_color: tuple = None
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            manager=manager,
            parent_panel=parent_panel,
            selectable=False,
            neighbors=None,
            layer=layer
        )

        self.style = StyleManager.current_style
        self._cell_bg = (40,40,40)
        self._cell_fg = (255,255,255)
        self.font = pygame.font.SysFont("Consolas", font_size)

        # Allow custom colors, fall back to style manager defaults
        self._text_color = text_color if text_color else self.style.text_color
        self._bg_color = bg_color if bg_color else self.style.bg_color

        # LCD grid
        self.lcd_col = 40
        self.lcd_row = 15
        self.lcd_grid = [[' ' for _ in range(self.lcd_col)] for _ in range(self.lcd_row)]
        self.current_row = 0

        # Gibberish source
        self.giberishDict = [
            ">Extruding Mesh Terrain", ">Inverting Career Ladder", ">Inserting Chaos Generator", ">Reticulating Splines",
            ">Iterating Chaos Array", ">Interpreting Family Values", ">Unfolding Helix Packet",">Spreading Rumors",
            ">Recycling Hex Decimals",">Simulating Program Execution",">Ensuring Transplanar Synergy",">Blurring Reality Lines",
            ">Destabilizing Orbital Payloads"
        ]

        # Cell size (computed later in render)
        self.cell_w = None
        self.cell_h = None

    # -----------------------
    # Text/Grid utilities
    # -----------------------

    def drawProgressBar(self, prompt, startingCol=0, progress=0):
        """
        Draws a progress bar on self.lcd_grid at the specified row.
        
        Args:
            prompt (str): Prompt above bar
            startingCol (int): Starting column. Default=0.
            progress (float): Progress (0.0 to 1.0). Default=0.
        
        Raises:
            ValueError: If row, startingCol, or progress is out of bounds.
        """
        # Get grid dimensions dynamically
        grid_rows = len(self.lcd_grid)
        grid_cols = len(self.lcd_grid[0]) if grid_rows > 0 else 0

        # Input validation
        if not (0 <= self.current_row < grid_rows):
            raise ValueError(f"Row must be between 0 and {grid_rows - 1}")
        if not (0 <= startingCol < grid_cols):
            raise ValueError(f"Starting column must be between 0 and {grid_cols - 1}")
        if not (0 <= progress <= 1):
            raise ValueError("Progress must be between 0 and 1")

        # Calculate available width for the progress bar (subtract 2 for the brackets)
        total_available_width = grid_cols - startingCol - 2  # For the brackets
        if total_available_width < 1:
            raise ValueError("Not enough columns for progress bar with brackets")
        
        filled_width = int(progress * total_available_width)
        remaining_width = total_available_width - filled_width

        # Print the prompt
        self.printText(prompt, row=self.current_row)

        # Construct the progress bar string with brackets
        progress_bar = '[' + ('#' * filled_width) + ('=' * remaining_width) + ']'

        # Ensure we don't exceed grid bounds
        end_col = startingCol + len(progress_bar)
        if end_col > grid_cols:
            progress_bar = progress_bar[:grid_cols - startingCol]

        # Update the row in self.lcd_grid
        progress_row = min(self.current_row + 1, grid_rows - 1)
        for col, char in enumerate(progress_bar, start=startingCol):
            if col < grid_cols:  # Prevent index overflow
                self.lcd_grid[progress_row][col] = char

    def getGiberishList(self,num_lines=3):
        """
        After 'loading', get some gibberish lines.
        Ensures no duplicate lines in a single call.
        """
        
        # Ensure we don't request more lines than available unique gibberish
        available_lines = min(num_lines, len(self.giberishDict))
        gib_lines = self.getGiberish(available_lines)
        return gib_lines
        
       

    def getGiberish(self, amount):
        """Return random gibberish strings without duplicates."""
        return random.sample(self.giberishDict, min(amount, len(self.giberishDict)))

    def printText(self, string, row=None):
        """
        Write a string into lcd_grid at given row.
        If row=None, use current_row and handle scrolling.
        """
        rows = len(self.lcd_grid)
        if rows == 0:
            return

        if row is None:
            row = self.current_row

        # Clamp string length to grid width
        max_cols = len(self.lcd_grid[0])
        for col, char in enumerate(string[:max_cols]):
            self.lcd_grid[row][col] = char


    def _advance_row(self):
        """
        Advances current_row, scrolling the lcd_grid if necessary.
        Always leaves the last 3 rows as an empty buffer.
        """
        rows = len(self.lcd_grid)
        buffer_rows = 3
        max_row = rows - buffer_rows - 1  # last row we can write to

        self.current_row += 1

        if self.current_row > max_row:
            # Shift all rows up by 1
            self.lcd_grid.pop(0)
            self.lcd_grid.append([' ' for _ in range(len(self.lcd_grid[0]))])

            # Clear the last buffer rows to ensure they stay empty
            for i in range(rows - buffer_rows, rows):
                self.lcd_grid[i] = [' ' for _ in range(len(self.lcd_grid[0]))]

            # Keep current_row fixed at max_row
            self.current_row = max_row


    # -----------------------
    # Render
    # -----------------------

    def render(self, screen: pygame.Surface):
        """Draws the whole lcd_grid as an LCD panel with gaps."""
        rows = len(self.lcd_grid)
        cols = len(self.lcd_grid[0]) if rows else 0
        if rows == 0 or cols == 0:
            return

        # Define gaps
        gap_x = 2  # horizontal gap
        gap_y = 1  # vertical gap

        # Effective drawable area (excluding total gaps)
        total_gap_w = (cols - 1) * gap_x
        total_gap_h = (rows - 1) * gap_y

        self.cell_w = (self.width - total_gap_w) // cols
        self.cell_h = (self.height - total_gap_h) // rows

        # Draw background
        pygame.draw.rect(screen, self._bg_color,
                        (self.x, self.y, self.width, self.height))

        # Draw each cell
        for r in range(rows):
            for c in range(cols):
                char = self.lcd_grid[r][c]

                # Calculate position with gaps
                draw_x = self.x + c * (self.cell_w + gap_x)
                draw_y = self.y + r * (self.cell_h + gap_y)

                self.drawLcdCell(screen, r, c, char, draw_x, draw_y)

    def drawLcdCell(self, screen, r, c, char, draw_x, draw_y):
        """Draw one LCD cell at given pixel position."""
        rect = pygame.Rect(draw_x, draw_y, self.cell_w, self.cell_h)

        # background
        pygame.draw.rect(screen, self._cell_bg, rect)

        # text (centered)
        text_surface = self.font.render(char, True, self._cell_fg)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    # -----------------------
    # Overrides
    # -----------------------

    def on_press(self):
        pass

    def set_position(self, x: int, y: int):
        self._explicit_x = x
        self._explicit_y = y

        if self.parent_panel:
            self.x = self.parent_panel.x + x
            self.y = self.parent_panel.y + y
        else:
            self.x = x
            self.y = y
