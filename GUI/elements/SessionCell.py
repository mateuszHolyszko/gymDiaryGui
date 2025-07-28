import pygame
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
        font_size: int = 16,
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
        self.excerciseTargetMuscle = Exercises.get_target_muscle(self.exercise) # Get based on excercise
        self.font = pygame.font.SysFont("Arial", font_size)
        self.edit_state = "notEdited"  # 'notEdited', 'editReps', 'editWeight', 'hasBeenEdited'
        self.has_been_edited = False
        self.is_active = False  # For input mode
        self.input_value = 0
        self.input_min = 0
        self.input_max = 100
        self.input_step_reps = 1
        self.input_step_weight = 1.25
        self.style = StyleManager.current_style

    def render(self, screen):
        # Draw background
        bg_color = self.style.bg_color
        pygame.draw.rect(screen, bg_color, (self.x, self.y, self.width, self.height))
        if self.is_focused:
            bg_color = self.style.highlight_color
        elif self.edit_state == "hasBeenEdited":
            bg_color = StyleManager.get_muscle_group_color(self.excerciseTargetMuscle)["bg_color"]
            bg_color = StyleManager.gray_out_color(bg_color, 0.4) 
        pygame.draw.rect(screen, bg_color, (self.x, self.y+self.height//2, self.width, self.height//2))
        # Draw border and divider
        pygame.draw.rect(screen, self.style.border_color, (self.x, self.y, self.width, self.height), 2)
        pygame.draw.line(screen, self.style.border_color, (self.x, self.y+self.height//2), (self.x+self.width, self.y+self.height//2), 2)
        # Top half: previous session
        if self.weightFromPreviousSession == 0 and self.repsFromPreviousSession == 0:
            header_text_bot = "New Set"
        else:
            header_text_bot = f"{self.weightFromPreviousSession}kg {self.repsFromPreviousSession}reps"
            
        header_surf = self.font.render(header_text_bot, True, self.style.text_color)
        screen.blit(header_surf, (self.x + (self.width-header_surf.get_width())//2, 
                self.y + (self.height//4+header_surf.get_height()//3)))
        # Divider in top Half
        pygame.draw.rect(screen, StyleManager.get_muscle_group_color(self.excerciseTargetMuscle)["bg_color"], (self.x, self.y, self.width, self.height//4))
        pygame.draw.line(screen, self.style.border_color, (self.x, self.y+self.height//4), (self.x+self.width, self.y+self.height//4), 2)
        header_text_top = self.excerciseTargetMuscle
        header_surf = self.font.render(header_text_top, True, (0,0,0))
        screen.blit(header_surf, (self.x + (self.width-header_surf.get_width())//2, self.y + (self.height//8-header_surf.get_height()//3)))
        # Bottom half: state-dependent
        if self.edit_state == "editReps":
            prompt = "Reps: "
            value = str(self.input_value)
            color = self.style.active_bg_color if self.is_active else self.style.bg_color
            pygame.draw.rect(screen, color, (self.x, self.y+self.height//2, self.width, self.height//2))
            text = self.font.render(prompt+value, True, self.style.text_color)
            screen.blit(text, (self.x + (self.width-text.get_width())//2, self.y+self.height//2 + (self.height//4-text.get_height()//2)))
        elif self.edit_state == "editWeight":
            prompt = "Weight: "
            value = str(self.input_value)
            color = self.style.active_bg_color if self.is_active else self.style.bg_color
            pygame.draw.rect(screen, color, (self.x, self.y+self.height//2, self.width, self.height//2))
            text = self.font.render(prompt+value, True, self.style.text_color)
            screen.blit(text, (self.x + (self.width-text.get_width())//2, self.y+self.height//2 + (self.height//4-text.get_height()//2)))
        elif self.edit_state == "notEdited":
            range_text = f"Range: {self.repRange[0]}-{self.repRange[1]}"
            text = self.font.render(range_text, True, self.style.text_color)
            screen.blit(text, (self.x + (self.width-text.get_width())//2, self.y+self.height//2 + (self.height//4-text.get_height()//2)))
        elif self.edit_state == "hasBeenEdited":
            # Create separate surfaces for weight and reps
            weight_text = self.font.render(f"{self.weightFromThisSession}kg", True, self.style.text_color)
            reps_text = self.font.render(f"{self.repsFromThisSession}reps", True, self.style.text_color)
            # Calculate positions
            total_height = weight_text.get_height() + reps_text.get_height()
            start_y = self.y + self.height//2 + (self.height//4 - total_height//2)
            # Draw weight (top)
            screen.blit(weight_text, 
                    (self.x + (self.width - weight_text.get_width())//2, 
                        start_y))
            # Draw reps (bottom)
            screen.blit(reps_text, 
                    (self.x + (self.width - reps_text.get_width())//2, 
                        start_y + weight_text.get_height()))

    def on_press(self):
        self.edit_state = "editReps"
        self.is_active = True
        self.input_value = self.repsFromThisSession
        self.input_min = 0
        self.input_max = 100
        self.input_step = 1
        self.manager.focus_manager.set_focus(self)

    def on_finished_edit(self):
        print(f"finished editing cell with values: {self.weightFromThisSession}kg, {self.repsFromThisSession} reps")

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.selectable:
            return False
        if self.edit_state == "editReps":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.repsFromThisSession = self.input_value
                    self.edit_state = "editWeight"
                    self.input_value = self.weightFromThisSession
                    self.input_min = 0
                    self.input_max = 1000
                    self.input_step = 1
                    self.is_active = True
                    return True
                elif event.key == pygame.K_TAB:
                    self.edit_state = "editWeight"
                    self.input_value = self.weightFromThisSession
                    self.input_min = 0
                    self.input_max = 1000
                    self.input_step = 1
                    self.is_active = True
                    return True
                elif event.key == pygame.K_LEFT or event.key == pygame.K_COMMA:
                    self.input_value = max(self.input_min, self.input_value - self.input_step)
                    return True
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_PERIOD:
                    self.input_value = min(self.input_max, self.input_value + self.input_step)
                    return True
        elif self.edit_state == "editWeight":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.weightFromThisSession = self.input_value
                    self.edit_state = "hasBeenEdited"
                    self.has_been_edited = True
                    self.is_active = False
                    self.on_finished_edit()
                    return True
                elif event.key == pygame.K_TAB:
                    self.weightFromThisSession = self.input_value
                    self.edit_state = "hasBeenEdited"
                    self.has_been_edited = True
                    self.is_active = False
                    self.on_finished_edit()
                    return True
                elif event.key == pygame.K_LEFT or event.key == pygame.K_COMMA:
                    self.input_value = max(self.input_min, self.input_value - self.input_step_weight)
                    return True
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_PERIOD:
                    self.input_value = min(self.input_max, self.input_value + self.input_step_weight)
                    return True
        elif self.edit_state == "notEdited":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.on_press()
                return True
            return super().handle_event(event)
        elif self.edit_state == "hasBeenEdited":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.edit_state = "editReps"
                self.is_active = True
                self.input_value = self.repsFromThisSession
                self.input_min = 0
                self.input_max = 100
                self.input_step = 1
                return True
            return super().handle_event(event)
        return False
