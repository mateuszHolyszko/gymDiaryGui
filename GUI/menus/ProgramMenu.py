import pygame
from GUI.Menu import Menu
from GUI.Panel import Panel
from GUI.panels.navigation_bar import NavigationBar
from GUI.elements.Button import Button
from GUI.elements.SelectDropDown import SelectDropDown
from GUI.Table import Table
from GUI.panels.ProgramMenu_ex_selection import TargetSelectionPanel
from GUI.elements.Image.Image2D_Graph import Image2D_Graph
from GUI.panels.ProgramMenu_stats_exercise import ExerciseStatsPanel
from workout_db_r.Target import Target

class ProgramMenu(Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_mode = "programs"  # Default mode, either "programs" or "exercises"

    def setup(self):
        """Setup panels, elements and actions"""
        screenWidth, screenHeight = pygame.display.get_surface().get_size() # Get screen size

        # Add navigation bar
        self.nav_bar = NavigationBar(manager=self.manager)
        self.add_panel_instance(self.nav_bar)

        # Chose PROGRAMS/EXERCISES panel
        self.programs_excercieses_panel = Panel(x=0, y=screenHeight - self.nav_bar.height - 50, width=screenWidth, height=50, layout_type="horizontal",manager=self.manager)
        self.add_panel_instance(self.programs_excercieses_panel)
        self.btn_ProgramMode = Button(width=screenWidth//8, height=35, text="Programs", manager=self.manager)
        self.btn_ExcerciseMode = Button(width=screenWidth//8, height=35, text="Excercises", manager=self.manager)
        self.programs_excercieses_panel.add_element(self.btn_ProgramMode)
        self.programs_excercieses_panel.add_element(self.btn_ExcerciseMode)
        self.btn_ProgramMode.activate()
        
        # Create choose programs panel, but dont add it to menu =====================================================================
        self.programsPanel = Panel(x=0, y=0, width=screenWidth//4, height=65,manager=self.manager)
        # Create table panel
        self.table = Table(x=self.programsPanel.width,y=0,width=screenWidth*3//4,height=self.programs_excercieses_panel.y,rows=3,cols=3,manager=self.manager)
        self.table.draw_table_lines = False 
        
        # Add elements
        programNames = self.manager.queryTool.get_all_program_names()
        self.selectProgram = SelectDropDown(options=programNames, width=self.programsPanel.width - 4, height=45, manager=self.manager, layer=2, drop_direction="down")
        self.programsPanel.add_element(self.selectProgram)

        self.table.load_data_program(self.manager.queryTool.get_program_table_data(programNames[0]),manager=self.manager) # Load initial program data

        # Excercises mode elements, but dont add it to menu:  =====================================================================
        self.targetSelectionPanel = TargetSelectionPanel(x=screenWidth - screenWidth//4,y=50, width=screenWidth//4, height=self.programs_excercieses_panel.y-50,manager=self.manager)
        self.targetSelectionPanel.getElements()[0].activate()  # Activate first button by default

        self.selectExercisePanel = Panel(x=0,y=0,width=screenWidth,height=50,manager=self.manager)
        self.selectExercise = SelectDropDown(options=self.manager.queryTool.get_exercise_names_by_target( self.targetSelectionPanel.active_target ), width=screenWidth//4, height=35, manager=self.manager, layer=3)
        self.selectExercisePanel.add_element(self.selectExercise)

        imagePanelWidth=self.targetSelectionPanel.x - 350 # 350 - stats panel width
        self.imagePanel = Panel(x=self.targetSelectionPanel.x - imagePanelWidth, y=self.targetSelectionPanel.y, width=imagePanelWidth, height=self.targetSelectionPanel.height,manager=self.manager)
        scale = 0.5
        self.image1 = Image2D_Graph(image_path="GUI\elements\Image\images\\Arm.png", height = 350*scale , width= 165*scale, manager=self.manager,layer=2, specificMuscleGroup=self.targetSelectionPanel.active_target )
        self.image1.muscleGroups = ["Shoulders","Biceps","Triceps","Forearms"]
        self.image2 = Image2D_Graph(image_path="GUI\elements\Image\images\\Leg.png", height = 350*scale , width= 210*scale, manager=self.manager,layer=2, specificMuscleGroup=self.targetSelectionPanel.active_target )
        self.image2.muscleGroups = ["Glutes","Quads","Hamstrings","Calves"]
        self.image3 = Image2D_Graph(image_path="GUI\elements\Image\images\\Torso.png", height = 350*scale , width= 291*scale, manager=self.manager,layer=2, specificMuscleGroup=self.targetSelectionPanel.active_target )
        self.image3.muscleGroups = ["Shoulders","Chest","Back","Abs"]
        self.imagePanel.add_element(self.image3) # Defult, since chest is the defult target

        self.statsPanel = ExerciseStatsPanel(x=0,y=self.targetSelectionPanel.y, width=350, height=self.programs_excercieses_panel.y-50,manager=self.manager,queriedExercise=self.selectExercise.getSelectedOption() )
        
        
        
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
        self.targetSelectionPanel.on_target_change = self.on_target_change
        self.selectExercise.on_finished_edit = self.on_finished_excercise_selection

    def remove_mode_panels(self):
        """Remove panels that are not navbar or programs/exercises panel"""
        self.remove_panels(except_panels=[self.nav_bar, self.programs_excercieses_panel])
        

    def load_program_mode(self, mode):

        # Remove all panels except navbar and programs/exercises panel
        self.remove_mode_panels()
        # Add panels relevant to program mode
        if mode == "programs":
            # Detatch possible connection between excercise btn and excercise mode content
            self.programs_excercieses_panel.getElements()[1].set_neighbor("up", None)

            # Add instances
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
            # Detatch possible connection between program btn and program mode content
            self.programs_excercieses_panel.getElements()[0].set_neighbor("up", None)

            # Add instances
            self.add_panel_instance(self.targetSelectionPanel)
            self.add_panel_instance(self.selectExercisePanel)
            self.add_panel_instance(self.imagePanel)
            self.add_panel_instance(self.statsPanel)

            # Connect PROGRAMS/EXERCISES panel and targetSelectionPanel
            self.targetSelectionPanel.getElements()[-1].set_neighbor("down", self.programs_excercieses_panel.getElements()[1])
            self.programs_excercieses_panel.getElements()[1].set_neighbor("up", self.targetSelectionPanel.getElements()[-1])

            # Connect targetSelectionPanel panel and selectExercisePanel
            self.selectExercisePanel.getElements()[-1].set_neighbor("down", self.targetSelectionPanel.getElements()[0])
            self.targetSelectionPanel.getElements()[0].set_neighbor("up", self.selectExercisePanel.getElements()[0])
            self.targetSelectionPanel.getElements()[1].set_neighbor("up", self.selectExercisePanel.getElements()[0]) # since there are 2 cols
        else:
            print("Invalid mode")


    def load_program(self):
        self.table.load_data_program(self.manager.queryTool.get_program_table_data( self.selectProgram.getSelectedOption() ),manager=self.manager)
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

    def on_target_change(self):
        self.selectExercise.updateOptions( self.manager.queryTool.get_exercise_names_by_target( self.targetSelectionPanel.active_target ) )
        self.on_finished_excercise_selection()
        self.imagePanel.clear_elements() # Clear previous image
        group =  Target.get_muscle_group(self.targetSelectionPanel.active_target)
        #group = Exercises.get_group_for_muscle(self.targetSelectionPanel.active_target)
        if group == "arms":
            self.imagePanel.add_element(self.image1)
        elif group == "legs":
            self.imagePanel.add_element(self.image2)
        else:
            self.imagePanel.add_element(self.image3)
        self.imagePanel.getElements()[0].updateSpecyficMuscleGroup( self.targetSelectionPanel.active_target ) 

    def on_finished_excercise_selection(self):
        self.statsPanel.queriedExercise = self.selectExercise.getSelectedOption()
        self.statsPanel.update()
