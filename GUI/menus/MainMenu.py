import pygame
from GUI.Menu import Menu
from GUI.Panel import Panel
from GUI.panels.navigation_bar import NavigationBar
from GUI.elements.Button import Button
from GUI.elements.SelectDropDown import SelectDropDown
from GUI.elements.Label import Label
from GUI.elements.InputField import InputField


class MainMenu(Menu):
    def setup(self):
        """Setup panels, elements and actions"""
        screenWidth, screenHeight = pygame.display.get_surface().get_size() # Get screen size

        # Add navigation bar
        self.nav_bar = self.add_panel(NavigationBar)
        
        # Create content panel
        self.content = self.add_panel(Panel, x=0, y=0, width=screenWidth//2, height=screenHeight - self.nav_bar.height)
        
        # Add elements
        self.inputField = InputField(initial_value=50, min_value=0, max_value=100, step=5, manager=self.manager)
        self.btn = Button("Button", width=200, height=50, manager=self.manager)
        options = ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5", "Option 6", "Option 7", "Option 8", "Option 9", "Option 10"]
        self.dropdown = SelectDropDown(options=options,width=200,height=50,manager=self.manager,layer=2)
        self.label = Label(text="Label", width=200, height=50, manager=self.manager)
        
        self.content.add_element(self.label)
        self.content.add_element(self.dropdown)
        self.content.add_element(self.inputField)
        self.content.add_element(self.btn)
        
        # Connect navigation between nav bar and content
        for nav_btn in self.nav_bar.buttons:
            nav_btn.set_neighbor("up", self.content.getElements()[-1])  # Last element in content
        self.content.getElements()[-1].set_neighbor("down", self.nav_bar.buttons[0])
        self.nav_bar.buttons[0].activate()

        # Connect neighbors within (can be done via panel or manualy)
        self.content.setNeighbors()
        
        # Set initial focus through manager
        self.set_initial_focus(self.nav_bar.buttons[0])
        
        # Set up actions
        self.setup_actions()
        
    def setup_actions(self):
        """Configure all element actions"""
        self.inputField.on_press = lambda: print(f"Selected value is {self.inputField.value}")
        self.btn.on_press = self.open_settings
        
        
    def open_settings(self):
        print("Opening settings...")
        self.label.editText( "Dropdown selection: " + self.dropdown.getSelectedOption())  # Example of using dropdown selection
        # Could switch to settings menu here