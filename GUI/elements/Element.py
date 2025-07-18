from abc import ABC, abstractmethod
import pygame

class Element(ABC):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        manager,
        parent_panel=None,
        selectable: bool = True,
        neighbors: dict = None,  # {"up": Element, "down": Element, ...}
        layer: int = 0  # Z-ordering layer for rendering
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.manager = manager
        self.parent_panel = parent_panel  # Reference to containing panel
        self.selectable = selectable
        self.neighbors = neighbors or {}  # Explicit navigation graph
        self.is_focused = False
        self.layer = layer

    @abstractmethod
    def render(self, screen: pygame.Surface):
        """Draws the element at its (x, y) with Z-ordering."""
        pass

    @abstractmethod
    def on_press(self):
        """Triggered when ENTER/SPACE is pressed on this element."""
        pass

    def position_from_center(self, center_x, center_y):
        """Position element relative to desired center point"""
        self.x = center_x - self.width//2
        self.y = center_y - self.height//2

    def set_neighbor(self, direction: str, element: 'Element'):
        """Updates a neighbor (e.g., set_neighbor("up", other_button))."""
        self.neighbors[direction] = element

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handles keyboard events using the focus manager"""
        if not self.selectable or not self.is_focused:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if hasattr(self, 'on_press'):
                    self.on_press()
                    return True
                    
            # Handle arrow key navigation
            elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                direction = {
                    pygame.K_UP: "up",
                    pygame.K_DOWN: "down",
                    pygame.K_LEFT: "left",
                    pygame.K_RIGHT: "right",
                }[event.key]
                neighbor = self.neighbors.get(direction)
                if neighbor and neighbor.selectable:
                    self.manager.focus_manager.set_focus(neighbor)
                    return True
                    
        return False