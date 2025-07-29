import pygame
from workout_db.programs_db import ProgramsDB
from GUI.Menu import Menu
from GUI.Panel import Panel
from GUI.panels.navigation_bar import NavigationBar
from GUI.elements.Button import Button
from GUI.elements.SelectDropDown import SelectDropDown
from GUI.Table import Table

class ProgramMenu(Menu):
    def setup(self):
        self.database = ProgramsDB()
        """Setup panels, elements and actions"""
        screenWidth, screenHeight = pygame.display.get_surface().get_size() # Get screen size

        # Add navigation bar
        self.nav_bar = self.add_panel(NavigationBar)
        
        # Create choose programs panel
        self.programsPanel = self.add_panel(Panel, x=0, y=0, width=screenWidth//4, height=screenHeight - self.nav_bar.height)
        # Create table panel
        self.table = self.add_panel(Table,
                                     x=screenWidth//4
                                     ,y=5
                                     ,width=screenWidth*3//4 - 5
                                     ,height=screenHeight - self.nav_bar.height - 10
                                     ,rows=3
                                     ,cols=3
                                     ,padding=10
                                     )
        self.table.draw_table_lines = False 
        
        # Add elements
        programNames = self.database.get_all_program_names()
        self.selectProgram = SelectDropDown(options=programNames, width=screenWidth//4, height=50, manager=self.manager, layer=2)
        self.programsPanel.add_element(self.selectProgram)

        self.table.load_data_program(self.database.get_program_data_as_table(programNames[0]),manager=self.manager) # Load initial program data
        
        
        # Connect navigation between nav bar and programsPanel
        for nav_btn in self.nav_bar.buttons:
            nav_btn.set_neighbor("up", self.programsPanel.getElements()[-1])  # Last element in programsPanel
        self.programsPanel.getElements()[-1].set_neighbor("down", self.nav_bar.buttons[0])

        # Connect navigation between programsPanel and table
        for programsPanel_elem in self.programsPanel.getElements():
            programsPanel_elem.set_neighbor("right", self.table.elements_grid[1][0])  # First element in table
        for row in self.table.elements_grid:
            for elem in row:
                if elem is not None:
                    elem.set_neighbor("left", self.programsPanel.getElements()[0])

        # Connect neighbors within (can be done via panel or manualy)
        self.programsPanel.setNeighbors()
        self.table.setNeighbors()
        
        # Set up actions
        self.setup_actions()
        
    def setup_actions(self):
        """Configure all element actions"""
        self.selectProgram.on_finished_edit = self.load_program

    def load_program(self):
        self.table.load_data_program(self.database.get_program_data_as_table( self.selectProgram.getSelectedOption() ),manager=self.manager)
        # Connect navigation between programsPanel and table
        for programsPanel_elem in self.programsPanel.getElements():
            programsPanel_elem.set_neighbor("right", self.table.elements_grid[1][0])  # First element in table
        for row in self.table.elements_grid:
            for elem in row:
                if elem is not None:
                    elem.set_neighbor("left", self.programsPanel.getElements()[0])
        self.table.setNeighbors()

    def set_initial_focus_on_switch(self):
        # Set focus to the first nav bar button or any default element
        self.set_initial_focus(self.nav_bar.buttons[2])
        self.nav_bar.buttons[2].activate()
