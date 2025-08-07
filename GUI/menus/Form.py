from GUI.Menu import Menu
from GUI.Panel import Panel
from GUI.panels.navigation_bar import NavigationBar
from GUI.elements.Button import Button
from GUI.elements.Label import Label
from workout_db.sessions_db import SessionsDB
from workout_db.programs_db import ProgramsDB
from datetime import datetime
import pygame

class Form(Menu):
    def setup(self):
        """Setup panels, elements and actions"""
        screenWidth, screenHeight = (800,480) # Get screen size
        self.session = SessionsDB()

        # Create choice_buttons_panel panel
        self.label_panel = self.add_panel(Panel, screenWidth//2 - screenWidth//4, 25, screenWidth//2, 50, layout_type="vertical")
        self.choice_buttons_panel = self.add_panel(Panel, screenWidth//2- screenWidth//4, 100, screenWidth//2, 50, layout_type="horizontal")
        
        # Add elements
        self.label = Label("Are you sure?",width=200, height=50, manager=self.manager)
        self.label_panel.add_element(self.label)

        self.yes_btn = Button("Yes", width=200, height=50, manager=self.manager)
        self.no_btn = Button("No", width=200, height=50, manager=self.manager)
        
        self.choice_buttons_panel.add_element(self.yes_btn)
        self.choice_buttons_panel.add_element(self.no_btn)
        
        # Connect navigation 
        self.choice_buttons_panel.setNeighbors()       
        
        # Set up actions
        self.setup_actions()
        
    def setup_actions(self):
        """Configure all element actions"""
        self.yes_btn.on_press = self.yes_pressed
        self.no_btn.on_press = self.no_pressed
        
        
    def yes_pressed(self):
        print("YES")
        JSONdata = self.manager.context["session_data"]
        print(JSONdata)
        self.session.add_session(JSONdata)
        self.manager.notification_system.show("Session saved successfully!", 3)
        self.manager.switch_to("MainMenu")
        
    def no_pressed(self):
        print("NO")
        self.manager.switch_to("SessionMenu")

    def set_initial_focus_on_switch(self):
        # Set focus to the first nav bar button or any default element
        self.set_initial_focus(self.choice_buttons_panel.getElements()[0])