import pygame
from GUI.Table import Table
from GUI.elements.Button import Button
from workout_db.exercises import Exercises
from GUI.style import StyleManager

class TargetSelectionPanel(Table):
    def __init__(self, x, y, width, height, manager):
        target_muscles = Exercises.getTargets()
        cols = 2
        rows = (len(target_muscles) + cols - 1) // cols  # Ceiling division

        super().__init__(x, y, width, height, manager, rows=rows, cols=cols)
        self.active_target = "Chest"

        # Fill the grid with muscle buttons
        for idx, muscle in enumerate(target_muscles):
            row = idx // cols
            col = idx % cols
            btn = Button(
                text=muscle,
                x=0, y=0,  # Will be positioned by Table
                width=width // cols,
                height=height // rows,
                manager=manager
            )
            # Set button color to match muscle group
            color_info = StyleManager.get_muscle_group_color(muscle)
            desaturate_color = StyleManager.gray_out_color(color_info['bg_color'], 0.8)  # Desaturate color for better visibility
            btn.set_style_override({'bg_color': desaturate_color})
            btn.set_style_override({'active_bg_color': color_info['bg_color']})
            btn.set_style_override({'text_color': (0, 0, 0)})
            self.add_element(btn, row, col)
            btn.on_press = self.on_button_press

        self.setNeighbors()
        self.enforceElementsSize()
        # if last cell is empty forcfully shift [-1] to middle
        if len(target_muscles) % cols != 0:
            self.getElements()[-1].x = self.x + self.width//2 - self.getElements()[-1].width//2
            self.getElements()[-2].set_neighbor("down", self.getElements()[-1])

    def on_button_press(self):
        print(f"target selected: {self.manager.focus_manager.current_focus.text}")
        for btns in self.getElements():
            btns.deactivate()
        self.manager.focus_manager.current_focus.activate()
        self.active_target = self.manager.focus_manager.current_focus.text
        self.on_target_change()

    def on_target_change(self):
        pass  # Overriden in menu
