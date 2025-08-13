from GUI.Form import Form
from GUI.elements.SelectDropDown import SelectDropDown
from GUI.elements.Label import Label
from GUI.Panel import Panel
import pygame

class FormGetExerciseOptions(Form):
    def __init__(self, screen, manager, return_menu_instance=None,selected_query=None):
        self.selected_query = selected_query
        super().__init__(screen, manager, return_menu_instance)

    def setup(self):
        """Setup panels, elements and actions"""
        screenWidth, screenHeight = pygame.display.get_surface().get_size() # Get screen size

        # Create exercise_selection_panel panel
        self.label_panel = self.add_panel(Panel, screenWidth//2 - screenWidth//4, 25, screenWidth//2, 50, layout_type="vertical")
        self.exercise_selection_panel = self.add_panel(Panel, screenWidth//2- screenWidth//6, 100, screenWidth//3, 50, layout_type="horizontal")
        
        # Add elements
        self.label = Label(text="Specyfic Exercise:",width=150, height=40, manager=self.manager)
        self.label_panel.add_element(self.label)
        
        self.exerciseDropDown = SelectDropDown(x=250,y=40,options=self.manager.queryTool.get_exercise_names_by_target(self.selected_query),manager=self.manager)
        self.exercise_selection_panel.add_element(self.exerciseDropDown)
        
        # Connect navigation 
        self.exercise_selection_panel.setNeighbors()       
        
        # Set up actions
        self.setup_actions()
        
    def setup_actions(self):
        """Configure all element actions"""
        self.exerciseDropDown.on_finished_edit = self.on_finished_edit

    def on_finished_edit(self):
        self.manager.notification_system.show(f"Exercise {self.exerciseDropDown.getSelectedOption()} choosen", 3)
        self.return_menu_instance.query = self.exerciseDropDown.getSelectedOption()
        self.return_menu_instance.update_ploter_on_edit_finished(self.selected_query)
        self.exit()
        print("exiting ex form")

    def set_initial_focus_on_switch(self):
        # Set focus to the first nav bar button or any default element
        self.set_initial_focus(self.exerciseDropDown)

    def getSelectedOption(self):
        return self.exerciseDropDown.getSelectedOption()