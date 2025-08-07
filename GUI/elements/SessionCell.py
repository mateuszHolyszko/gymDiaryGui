import pygame
import pyglet
from .Element import Element
from GUI.style import StyleManager
from workout_db.exercises import Exercises

class SessionCell(Element):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 100,
        manager=None,
        parent_panel=None,
        selectable: bool = True,
        neighbors: dict = None,
        font_size: int = 14,
        layer: int = 0,
        weight_previous: float = 0,
        reps_previous: int = 1,
        rep_range: tuple = (1, 2),
        exercise: str = "Squat"
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
        self.weightFromPreviousSession = weight_previous
        self.weightFromThisSession = weight_previous
        self.repsFromPreviousSession = reps_previous
        self.repsFromThisSession = reps_previous
        self.repRange = rep_range
        self.exercise = exercise
        self.excerciseTargetMuscle = Exercises.get_target_muscle(self.exercise)
        self.font_size = font_size
        self.edit_state = "notEdited"
        self.has_been_edited = False
        self.is_active = False
        self.input_value_reps = self.repsFromThisSession
        self.input_value_weight = self.weightFromThisSession
        self.input_min = 0
        self.input_max = 100
        self.input_step_reps = 1
        self.input_step_weight = 1.25
        self.style = StyleManager.current_style

    def render(self, batch):
        style = self.style
        bg_color = style.bg_color
        if self.is_focused:
            bg_color = style.highlight_color
        elif self.edit_state == "hasBeenEdited":
            bg_color = StyleManager.get_muscle_group_color(self.excerciseTargetMuscle)["bg_color"]
            bg_color = StyleManager.gray_out_color(bg_color, 0.4)
        pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, color=bg_color[:3], batch=batch)
        # Border and divider
        pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, color=style.border_color[:3], batch=batch)
        pyglet.shapes.Line(self.x, self.y+self.height//2, self.x+self.width, self.y+self.height//2, width=2, color=style.border_color[:3], batch=batch)
        # Top half: previous session
        if self.weightFromPreviousSession == 0 and self.repsFromPreviousSession == 0:
            header_text_bot = "New Set"
        else:
            header_text_bot = f"{self.weightFromPreviousSession}kg {self.repsFromPreviousSession}reps"
        pyglet.text.Label(
            header_text_bot,
            font_name='Arial',
            font_size=self.font_size,
            color=style.text_color + (255,),
            x=self.x + self.width // 2,
            y=self.y + self.height // 4,
            anchor_x='center',
            anchor_y='center',
            batch=batch
        )
        # Divider in top Half
        muscle_color = StyleManager.get_muscle_group_color(self.excerciseTargetMuscle)["bg_color"]
        pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height//4, color=muscle_color[:3], batch=batch)
        pyglet.shapes.Line(self.x, self.y+self.height//4, self.x+self.width, self.y+self.height//4, width=2, color=style.border_color[:3], batch=batch)
        pyglet.text.Label(
            self.excerciseTargetMuscle,
            font_name='Arial',
            font_size=self.font_size,
            color=(0,0,0,255),
            x=self.x + self.width // 2,
            y=self.y + self.height // 8,
            anchor_x='center',
            anchor_y='center',
            batch=batch
        )
        # Bottom half: state-dependent
        if self.edit_state == "editReps":
            prompt = "Reps: "
            value = str(self.input_value_reps)
            color = style.active_bg_color if self.is_active else style.bg_color
            pyglet.shapes.Rectangle(self.x, self.y+self.height//2, self.width, self.height//2, color=color[:3], batch=batch)
            pyglet.text.Label(
                prompt+value,
                font_name='Arial',
                font_size=self.font_size,
                color=style.text_color + (255,),
                x=self.x + self.width // 2,
                y=self.y + 3*self.height // 4,
                anchor_x='center',
                anchor_y='center',
                batch=batch
            )
        elif self.edit_state == "editWeight":
            prompt = "Weight: "
            value = str(self.input_value_weight)
            color = style.active_bg_color if self.is_active else style.bg_color
            pyglet.shapes.Rectangle(self.x, self.y+self.height//2, self.width, self.height//2, color=color[:3], batch=batch)
            pyglet.text.Label(
                prompt+value,
                font_name='Arial',
                font_size=self.font_size,
                color=style.text_color + (255,),
                x=self.x + self.width // 2,
                y=self.y + 3*self.height // 4,
                anchor_x='center',
                anchor_y='center',
                batch=batch
            )
        elif self.edit_state == "notEdited":
            range_text = f"Range: {self.repRange[0]}-{self.repRange[1]}"
            pyglet.text.Label(
                range_text,
                font_name='Arial',
                font_size=self.font_size,
                color=style.text_color + (255,),
                x=self.x + self.width // 2,
                y=self.y + 3*self.height // 4,
                anchor_x='center',
                anchor_y='center',
                batch=batch
            )
        elif self.edit_state == "hasBeenEdited":
            # Draw weight and reps
            weight_str = f"{self.weightFromThisSession}kg"
            reps_str = f"{self.repsFromThisSession}reps"
            pyglet.text.Label(
                weight_str,
                font_name='Arial',
                font_size=self.font_size,
                color=style.text_color + (255,),
                x=self.x + self.width // 2,
                y=self.y + 3*self.height // 4 + self.font_size//2,
                anchor_x='center',
                anchor_y='center',
                batch=batch
            )
            pyglet.text.Label(
                reps_str,
                font_name='Arial',
                font_size=self.font_size,
                color=style.text_color + (255,),
                x=self.x + self.width // 2,
                y=self.y + 3*self.height // 4 - self.font_size//2,
                anchor_x='center',
                anchor_y='center',
                batch=batch
            )
        batch.draw()

    def on_press(self):
        self.edit_state = "editReps"
        self.is_active = True
        #self.input_value_reps = self.repsFromThisSession
        self.input_min = 0
        self.input_max = 100
        self.input_step = 1
        self.manager.focus_manager.set_focus(self)

    def on_finished_edit(self):
        print(f"finished editing cell with values: {self.weightFromThisSession}kg, {self.repsFromThisSession} reps")

    def handle_event(self, event) -> bool:
        if not self.selectable:
            return False
        from pyglet.window import key
        if self.edit_state == "editReps":
            if getattr(event, 'type', None) == 'KEYDOWN':
                if event.symbol == key.RETURN:
                    self.repsFromThisSession = self.input_value_reps
                    self.edit_state = "editWeight"
                    self.input_min = 0
                    self.input_max = 1000
                    self.input_step = 1
                    self.is_active = True
                    return True
                elif event.symbol == key.TAB:
                    self.edit_state = "editWeight"
                    self.input_min = 0
                    self.input_max = 1000
                    self.input_step = 1
                    self.is_active = True
                    return True
                elif event.symbol in (key.LEFT, key.COMMA):
                    self.input_value_reps = max(self.input_min, self.input_value_reps - self.input_step_reps)
                    return True
                elif event.symbol in (key.RIGHT, key.PERIOD):
                    self.input_value_reps = min(self.input_max, self.input_value_reps + self.input_step_reps)
                    return True
        elif self.edit_state == "editWeight":
            if getattr(event, 'type', None) == 'KEYDOWN':
                if event.symbol == key.RETURN:
                    self.weightFromThisSession = self.input_value_weight
                    self.edit_state = "hasBeenEdited"
                    self.has_been_edited = True
                    self.is_active = False
                    self.on_finished_edit()
                    return True
                elif event.symbol == key.TAB:
                    self.weightFromThisSession = self.input_value_weight
                    self.edit_state = "hasBeenEdited"
                    self.has_been_edited = True
                    self.is_active = False
                    self.on_finished_edit()
                    return True
                elif event.symbol in (key.LEFT, key.COMMA):
                    self.input_value_weight = max(self.input_min, self.input_value_weight - self.input_step_weight)
                    return True
                elif event.symbol in (key.RIGHT, key.PERIOD):
                    self.input_value_weight = min(self.input_max, self.input_value_weight + self.input_step_weight)
                    return True
        elif self.edit_state == "notEdited":
            if getattr(event, 'type', None) == 'KEYDOWN' and event.symbol == key.RETURN:
                self.on_press()
                return True
            return super().handle_event(event)
        elif self.edit_state == "hasBeenEdited":
            if getattr(event, 'type', None) == 'KEYDOWN' and event.symbol == key.RETURN:
                self.edit_state = "editReps"
                self.is_active = True
                self.input_value_reps = self.repsFromThisSession
                self.input_min = 0
                self.input_max = 100
                self.input_step = 1
                return True
            return super().handle_event(event)
        return False
