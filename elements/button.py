from .base import Element
import pygame

class Button(Element):
    def __init__(self, name, text, x=0, y=0, width=100, height=30, on_press=None, selectable=True):
        super().__init__(name, x, y, width, height, selectable=selectable, text=text)
        self.on_press = on_press
        self.activated = False  # Activation state
        self.activated_color = (0, 100, 200)  # Blue color for activated state
        self.activated_border = (0, 150, 255)  # Lighter blue border

    def on_key(self, event):
        if not self.selectable:
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.emit("pressed", self.text)  # Emit signal
            print(f"Button '{self.text}' pressed!")
            if self.on_press:
                self.on_press()

    def render(self, surface, path, font, x=None, y=None, width=None, height=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        width = self.width if width is None else width
        height = self.height if height is None else height

        if not self.selectable:
            # Render as grayed out/unselectable
            fill_color = (80, 80, 80)
            border_color = (120, 120, 120)
            text_color = (180, 180, 180)
        elif self.activated:
            # Activated state rendering
            is_focused = self is path[-1]
            border_color = self.activated_border
            fill_color = (self.activated_color[0] + 50, 
                         self.activated_color[1] + 50, 
                         self.activated_color[2] + 50) if is_focused else self.activated_color
            text_color = (255, 255, 255)
        else:
            # Normal state rendering
            is_focused = self is path[-1]
            border_color = (0, 255, 0) if self in path else (255, 255, 255)
            fill_color = (50, 150, 50) if is_focused else (0, 0, 0)
            text_color = (255, 255, 255)

        pygame.draw.rect(surface, fill_color, (x, y, width, height))
        pygame.draw.rect(surface, border_color, (x, y, width, height), 2)
        self.render_text(surface, font, x, y, width, height, color=text_color)