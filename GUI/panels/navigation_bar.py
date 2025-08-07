import pygame
from GUI.Panel import Panel
from GUI.elements.Button import Button
from GUI.elements.Clock import Clock

class NavigationBar(Panel):
    def __init__(self, manager, **kwargs):  # manager as explicit first argument
        # Calculate position (bottom of screen)
        screen_width, screen_height = pygame.display.get_surface().get_size()
        super().__init__(
            x=0,
            y=screen_height - 50,
            width=screen_width,
            height=50,
            manager=manager,  # Pass to Panel
            layout_type="horizontal",
            **kwargs  # Pass any additional arguments
        )
        self.buttons = [
            Button("Main", width=100, height=40, manager=self.manager),
            Button("Session", width=100, height=40, manager=self.manager),
            Button("Program", width=100, height=40, manager=self.manager),
            Button("Stats", width=100, height=40, manager=self.manager)
        ]

        self.clock = Clock(width=100, height=40, manager=self.manager)
        
        # Add buttons to panel
        for btn in self.buttons:
            self.add_element(btn)

        # Add clock to panel
        self.add_element(self.clock)
        
        # Setup neighbors
        for i in range(len(self.buttons)-1):
            self.buttons[i].set_neighbor("right", self.buttons[i+1])
            self.buttons[i+1].set_neighbor("left", self.buttons[i])
        
        # Setup actions
        self.buttons[0].on_press = lambda: manager.switch_to("MainMenu")
        self.buttons[1].on_press = lambda: manager.switch_to("SessionMenu")
        self.buttons[2].on_press = lambda: manager.switch_to("ProgramMenu")
        self.buttons[3].on_press = lambda: manager.switch_to("StatsMenu")