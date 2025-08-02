import pygame
from workout_db.programs_db import ProgramsDB
from GUI.Menu import Menu
from GUI.Panel import Panel
from GUI.panels.navigation_bar import NavigationBar
from GUI.elements.Button import Button
from GUI.elements.SelectDropDown import SelectDropDown
from GUI.Table import Table

class ProgramMenu(Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_mode = "programs"  # Default mode, either "programs" or "exercises"

    def setup(self):
        self.database = ProgramsDB()
        """Setup panels, elements and actions"""
        screenWidth, screenHeight = pygame.display.get_surface().get_size() # Get screen size

        # Add navigation bar
        self.nav_bar = NavigationBar(manager=self.manager)
        self.add_panel_instance(self.nav_bar)

        # Chose PROGRAMS/EXERCISES panel
        self.programs_excercieses_panel = Panel(x=0, y=screenHeight - self.nav_bar.height - 50, width=screenWidth, height=50, layout_type="horizontal",manager=self.manager)
        self.add_panel_instance(self.programs_excercieses_panel)
        self.btn_ProgramMode = Button(width=screenWidth//6, height=50, text="Programs", manager=self.manager)
        self.btn_ExcerciseMode = Button(width=screenWidth//6, height=50, text="Excercises", manager=self.manager)
        self.programs_excercieses_panel.add_element(self.btn_ProgramMode)
        self.programs_excercieses_panel.add_element(self.btn_ExcerciseMode)
        self.btn_ProgramMode.activate()
        
        # Create choose programs panel, but dont add it to menu =====================================================================
        heightOfProgPanel = screenHeight - self.nav_bar.height - self.programs_excercieses_panel.height
        self.programsPanel = Panel(x=0, y=self.programs_excercieses_panel.height, width=screenWidth//4, height=heightOfProgPanel,manager=self.manager)
        # Create table panel
        self.table = Table(x=screenWidth//4,y=5,width=screenWidth*3//4 - 5,height=heightOfProgPanel,rows=3,cols=3,padding=10,manager=self.manager)
        self.table.draw_table_lines = False 
        
        # Add elements
        programNames = self.database.get_all_program_names()
        self.selectProgram = SelectDropDown(options=programNames, width=screenWidth//4, height=50, manager=self.manager, layer=2)
        self.programsPanel.add_element(self.selectProgram)

        self.table.load_data_program(self.database.get_program_data_as_table(programNames[0]),manager=self.manager) # Load initial program data

        # Excercises mode elements, but dont add it to menu:  =====================================================================

        
        
        # Connect navigation between nav bar and PROGRAMS/EXERCISES panel
        for nav_btn in self.nav_bar.buttons:
            nav_btn.set_neighbor("up", self.programs_excercieses_panel.getElements()[0])  # First element in programs_excercieses_panel
        for btn in self.programs_excercieses_panel.getSelectableElements():
            btn.set_neighbor("down", self.nav_bar.buttons[2])

        # Connect neighbors within (can be done via panel or manualy)
        self.programs_excercieses_panel.setNeighbors()
        self.programsPanel.setNeighbors()
        self.table.setNeighbors()

        self.load_program_mode("programs")  # Load default mode
        
        # Set up actions
        self.setup_actions()
        
    def setup_actions(self):
        """Configure all element actions"""
        self.selectProgram.on_finished_edit = self.load_program
        self.btn_ProgramMode.on_press = self.on_press_program_mode
        self.btn_ExcerciseMode.on_press = self.on_press_excercise_mode

    def remove_mode_panels(self):
        """Remove panels that are not navbar or programs/exercises panel"""
        self.remove_panels(except_panels=[self.nav_bar, self.programs_excercieses_panel])
        

    def load_program_mode(self, mode):

        # Remove all panels except navbar and programs/exercises panel
        self.remove_mode_panels()
        # Add panels relevant to program mode
        if mode == "programs":
            self.add_panel_instance(self.programsPanel)
            self.add_panel_instance(self.table)

            # Connect navigation between programsPanel and table
            for programsPanel_elem in self.programsPanel.getElements():
                programsPanel_elem.set_neighbor("right", self.table.elements_grid[1][0])  # First element in table
            for row in self.table.elements_grid:
                for elem in row:
                    if elem is not None:
                        elem.set_neighbor("left", self.programsPanel.getElements()[0])
            # Connect PROGRAMS/EXERCISES panel and programsPanel
            self.selectProgram.set_neighbor("down", self.programs_excercieses_panel.getElements()[0])
            self.programs_excercieses_panel.getElements()[0].set_neighbor("up", self.selectProgram)

        elif mode == "exercises":
            print("TODO")
        else:
            print("Invalid mode")


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

    def on_press_program_mode(self):
        self.btn_ProgramMode.activate()
        self.btn_ExcerciseMode.deactivate()
        self.load_program_mode("programs")

    def on_press_excercise_mode(self):
        self.btn_ProgramMode.deactivate()
        self.btn_ExcerciseMode.activate()
        self.load_program_mode("exercises")
