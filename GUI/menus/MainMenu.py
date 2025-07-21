import pygame
from GUI.Menu import Menu
from GUI.Panel import Panel
from GUI.panels.navigation_bar import NavigationBar
from GUI.elements.Button import Button
from GUI.elements.SelectDropDown import SelectDropDown
from GUI.elements.Label import Label
from GUI.elements.InputField import InputField
from GUI.Table import Table
from workout_db.programs_db import ProgramsDB
from GUI.elements.SessionCell import SessionCell


class MainMenu(Menu):
    def setup(self):
        self.database = ProgramsDB()
        """Setup panels, elements and actions"""
        screenWidth, screenHeight = pygame.display.get_surface().get_size() # Get screen size

        # Add navigation bar
        self.nav_bar = self.add_panel(NavigationBar)
        
        # Create content panel
        self.content = self.add_panel(Panel, x=0, y=0, width=screenWidth//2, height=screenHeight - self.nav_bar.height)
        # Create table panel
        self.table = self.add_panel(Table,
                                     x=screenWidth//2
                                     ,y=5
                                     ,width=screenWidth//2 - 5
                                     ,height=screenHeight - self.nav_bar.height - 10
                                     ,rows=3
                                     ,cols=3
                                     ,padding=10
                                     )
        self.table.draw_table_lines = False 
        
        # Add elements (content panel)
        self.inputField = InputField(initial_value=50, min_value=0, max_value=100, step=5, manager=self.manager)
        self.btn = Button("Button", width=200, height=50, manager=self.manager)
        options = ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5", "Option 6", "Option 7", "Option 8", "Option 9", "Option 10"]
        self.dropdown = SelectDropDown(options=options,width=200,height=50,manager=self.manager,layer=2)
        self.label = Label(text="Label", width=200, height=50, manager=self.manager)
        
        self.content.add_element(self.label)
        self.content.add_element(self.dropdown)
        self.content.add_element(self.inputField)
        self.content.add_element(self.btn)

        # Add elements (table panel)
        # Add header labels
        self.table.add_element(Label("Name", width=120, height=40, manager=self.manager), 0, 0)
        self.table.add_element(Label("Age", width=120, height=40, manager=self.manager), 0, 1)
        self.table.add_element(Label("Action", width=120, height=40, manager=self.manager), 0, 2)

        # Add input fields for row 1
        self.table.add_element(InputField(initial_value=0, width=120, height=40, manager=self.manager), 1, 0)
        self.table.add_element(InputField(initial_value=18, width=120, height=40, manager=self.manager), 1, 1)
        self.table.add_element(Button("Submit", width=120, height=40, manager=self.manager), 1, 2)

        # Add another row (could be more input fields, labels, or buttons)
        self.table.add_element(Label("Row 2", width=120, height=40, manager=self.manager), 2, 0)
        self.table.add_element(InputField(initial_value=25, width=120, height=40, manager=self.manager), 2, 1)
        self.table.add_element(SessionCell( manager=self.manager,parent_panel=self.table), 2, 2)

        #self.table.enforceElementsSize()  # Ensure elements fit in their cells
        
        # Connect navigation between nav bar and content
        for nav_btn in self.nav_bar.buttons:
            nav_btn.set_neighbor("up", self.content.getElements()[-1])  # Last element in content
        self.content.getElements()[-1].set_neighbor("down", self.nav_bar.buttons[0])
        self.nav_bar.buttons[0].activate()

        # Connect navigation between content and table
        for content_btn in self.content.getElements():
            content_btn.set_neighbor("right", self.table.elements_grid[1][0])  # First element in table
        self.table.elements_grid[1][0].set_neighbor("left", self.content.getElements()[1])

        # Connect neighbors within (can be done via panel or manualy)
        self.content.setNeighbors()
        self.table.setNeighbors()
        
        # Set initial focus through manager
        self.set_initial_focus(self.nav_bar.buttons[0])
        #self.set_initial_focus(self.table.elements_grid[1][0])  # Focus on first input field in table
        
        # Set up actions
        self.setup_actions()
        
    def setup_actions(self):
        """Configure all element actions"""
        self.inputField.on_press = lambda: print(f"Selected value is {self.inputField.value}")
        self.btn.on_press = self.open_settings
        
        
    def open_settings(self):
        print("Opening settings...")
        self.label.editText( "Dropdown selection: " + self.dropdown.getSelectedOption())  # Example of using dropdown selection
        self.inputField.getInput(self.screen)
        # Could switch to settings menu here