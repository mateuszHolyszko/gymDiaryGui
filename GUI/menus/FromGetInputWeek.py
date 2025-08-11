from GUI.Form import Form
from GUI.elements.InputField import InputField
from GUI.elements.Label import Label
from GUI.Panel import Panel
import pygame

class FormGetInputWeek(Form):
    def setup(self):
        """Setup panels, elements and actions"""
        screenWidth, screenHeight = pygame.display.get_surface().get_size() # Get screen size

        # Create weekInputField_panel panel
        self.label_panel = self.add_panel(Panel, screenWidth//2 - screenWidth//4, 25, screenWidth//2, 50, layout_type="vertical")
        self.weekInputField_panel = self.add_panel(Panel, screenWidth//2- screenWidth//8, 100, screenWidth//4, 50, layout_type="horizontal")
        
        # Add elements
        self.label = Label(text="How many weeks to query:",width=200, height=40, manager=self.manager)
        self.label_panel.add_element(self.label)

        self.weekInputField = InputField(initial_value=1, min_value=1, max_value=12, step=1, manager=self.manager,x=screenWidth//2-40,y=screenHeight//2) # Get max value from db?
        self.weekInputField_panel.add_element(self.weekInputField)
        
        # Connect navigation 
        self.weekInputField_panel.setNeighbors()       
        
        # Set up actions
        self.setup_actions()
        
    def setup_actions(self):
        """Configure all element actions"""
        self.weekInputField.on_press = self.on_press

    def on_press(self):
        print(f"pressed {self.getValue()}")
        self.return_menu_instance.update_weeks()
        self.exit()

    def set_initial_focus_on_switch(self):
        # Set focus to the first nav bar button or any default element
        self.set_initial_focus(self.weekInputField)
        self.weekInputField.is_active = True # Edit it by defult so we dont have to press enter

    def getValue(self):
        return self.weekInputField.value