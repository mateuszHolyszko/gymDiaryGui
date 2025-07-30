from GUI.Menu import Menu
from GUI.Panel import Panel
from GUI.panels.navigation_bar import NavigationBar
from GUI.elements.Button import Button
from workout_db.programs_db import ProgramsDB
from workout_db.sessions_db import SessionsDB
from GUI.elements.SelectDropDown import SelectDropDown
from workout_db.exercises import Exercises
import pygame
from GUI.elements.Plotter import Plotter

class StatsMenu(Menu):
    def setup(self):
        """Setup panels, elements and actions"""
        self.database = ProgramsDB()
        self.session = SessionsDB()

        screenWidth, screenHeight = pygame.display.get_surface().get_size() # Get screen size

        # Add navigation bar
        self.nav_bar = self.add_panel(NavigationBar)
        
        # Create queryTypePanel panel
        self.queryTypePanel = self.add_panel(Panel, x=0,y=self.nav_bar.y-(screenHeight// 6), width=screenWidth, height=screenHeight// 6, layout_type="horizontal")
        # Create queryAxisPanel panel
        self.queryAxisPanel = self.add_panel(Panel, x=0,y=0, width=screenWidth//5, height=screenHeight-self.nav_bar.height-self.queryTypePanel.height, layout_type="vertical")
        # Create plotter panel
        self.PlotterPanel = self.add_panel(Panel, x=screenWidth//5,y=0, width=screenWidth-screenWidth//5, height=screenHeight-self.nav_bar.height-self.queryTypePanel.height)
        
        # Add queryTypePanel elements
        list_of_queries = Exercises.getTargets()
        list_of_queries.append("Weight")
        
        self.query_btn = SelectDropDown(list_of_queries, width=200, height=25, manager=self.manager,drop_direction="up",layer=2)
        self.weeks_btn = Button("Weeks", width=200, height=25, manager=self.manager)
        
        self.queryTypePanel.add_element(self.query_btn)
        self.queryTypePanel.add_element(self.weeks_btn)

        # Add queryAxisPanel elements
        self.Yaxis_weight_btn = Button("KG",width=100, height=50, manager=self.manager)
        self.Yaxis_reps_btn = Button("Reps",width=100, height=50, manager=self.manager)
        self.Yaxis_volume_btn = Button("Vol",width=100, height=50, manager=self.manager)

        self.queryAxisPanel.add_element(self.Yaxis_weight_btn)
        self.queryAxisPanel.add_element(self.Yaxis_reps_btn)
        self.queryAxisPanel.add_element(self.Yaxis_volume_btn)

        # Add plotter
        import math
        x_vals = [i * 0.1 for i in range(63)]
        y_vals = [math.sin(x) for x in x_vals]

        plotter = Plotter(
            x_values=x_vals,
            y_values=y_vals,
            x=0,
            y=0,
            width=self.PlotterPanel.width,
            height=self.PlotterPanel.height,
            y_label="Amplitude",
            x_label="Time (s)"
        )
        self.PlotterPanel.add_element(plotter)
        
        # Connect navigation between nav bar and queryTypePanel
        for nav_btn in self.nav_bar.buttons:
            nav_btn.set_neighbor("up", self.query_btn)
        for element in self.queryTypePanel.getElements():
            element.set_neighbor("down", self.nav_bar.buttons[3])
        self.nav_bar.buttons[3].activate()

        # Connect queryTypePanel and queryAxisPanel
        for type_btn in self.queryTypePanel.getElements():
            type_btn.set_neighbor("up", self.queryAxisPanel.getSelectableElements()[-1])
        self.queryAxisPanel.getElements()[-1].set_neighbor("down", self.queryTypePanel.getElements()[0])

        self.queryTypePanel.setNeighbors()
        self.queryAxisPanel.setNeighbors()
        
        # Set up actions
        self.setup_actions()
        
    def setup_actions(self):
        """Configure all element actions"""
        self.query_btn.on_finished_edit = self.load_query
        self.weeks_btn.on_press = self.load_weeks

    def load_query(self):
        selected_query = self.query_btn.getSelectedOption()
        # check if muscle group was selected, if so, need to ask for a specifice excercise in a form
        if selected_query in Exercises.getTargets():
            # Form
            pass
        elif selected_query == "Weight":
            # Load weight query
            pass
        else:
            print(f"Selected query: {selected_query} is unhandeled.")

    
    def load_weeks(self):
        pass
        

    def set_initial_focus_on_switch(self):
        # Set focus to the first nav bar button or any default element
        self.set_initial_focus(self.nav_bar.buttons[3])
        self.nav_bar.buttons[3].activate()