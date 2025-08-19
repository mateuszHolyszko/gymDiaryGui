from GUI.Menu import Menu
from GUI.Panel import Panel
from GUI.panels.navigation_bar import NavigationBar
from GUI.elements.Button import Button
from GUI.elements.SelectDropDown import SelectDropDown
from GUI.menus.FromGetInputWeek import FormGetInputWeek
import pygame
from GUI.elements.Plotter import Plotter
from GUI.style import StyleManager
from GUI.menus.FormGetExerciseOptions import FormGetExerciseOptions

class StatsMenu(Menu):
    def setup(self):
        """Setup panels, elements and actions"""
        # Plotter values
        self.x_vals = []
        self.y_vals = []
        self.query = None
        self.queryAxisY = "weight"  # Default Y axis value

        self.screenWidth, self.screenHeight = pygame.display.get_surface().get_size() # Get screen size

        # Add navigation bar
        self.nav_bar = self.add_panel(NavigationBar)
        
        # Create queryTypePanel panel
        self.queryTypePanel = self.add_panel(Panel, x=0,y=self.nav_bar.y-(self.screenHeight// 6), width=self.screenWidth, height=self.screenHeight// 6, layout_type="horizontal")
        # Create queryAxisPanel panel
        self.queryAxisPanel = self.add_panel(Panel, x=0,y=0, width=self.screenWidth//5, height=self.screenHeight-self.nav_bar.height-self.queryTypePanel.height, layout_type="vertical")
        # Create plotter panel
        self.PlotterPanel = self.add_panel(Panel, x=self.screenWidth//5,y=0, width=self.screenWidth-self.screenWidth//5, height=self.screenHeight-self.nav_bar.height-self.queryTypePanel.height)
        
        # Add queryTypePanel elements
        list_of_queries = self.manager.queryTool.get_all_targets()
        list_of_queries.append("weight")
        
        self.query_btn = SelectDropDown(list_of_queries, width=200, height=25, manager=self.manager,drop_direction="up",layer=2)
        # Input field wont be appended to panel since it will be used for getInput() method
        
        self.week_input_form = FormGetInputWeek(screen=self.screen,manager=self.manager, return_menu_instance=self) 
        self.weeks_btn = Button(f"Search in {self.week_input_form.getValue()} Weeks", width=200, height=25, manager=self.manager)
        
        self.queryTypePanel.add_element(self.query_btn)
        self.queryTypePanel.add_element(self.weeks_btn)

        # Add queryAxisPanel elements
        self.Yaxis_weight_btn = Button("Kg",width=100, height=50, manager=self.manager)
        self.Yaxis_reps_btn = Button("Reps",width=100, height=50, manager=self.manager)
        self.Yaxis_volume_btn = Button("Vol",width=100, height=50, manager=self.manager)

        self.queryAxisPanel.add_element(self.Yaxis_weight_btn)
        self.queryAxisPanel.add_element(self.Yaxis_reps_btn)
        self.queryAxisPanel.add_element(self.Yaxis_volume_btn)

        # Add plotter
        # Get data for plotter
        self.query = self.query_btn.getSelectedOption()
        
        self.plotter = Plotter(
            x_values=[],
            y_values=[],
            x=0,
            y=0,
            width=self.PlotterPanel.width,
            height=self.PlotterPanel.height,
            y_label="Amplitude",
            x_label="Date"
        )
        self.PlotterPanel.add_element(self.plotter)
        
        # Connect navigation between nav bar and queryTypePanel
        for nav_btn in self.nav_bar.buttons:
            nav_btn.set_neighbor("up", self.query_btn)
        for element in self.queryTypePanel.getElements():
            element.set_neighbor("down", self.nav_bar.buttons[3])
        self.nav_bar.buttons[3].activate()

        self.queryTypePanel.setNeighbors()

        # Connect queryTypePanel and queryAxisPanel
        # Dont do it here, since it will change based on QueryValueType, and will be set there dynamicly

        self.load_query_type() # This sets the data, and configures the buttons
        
        # Set up actions
        self.setup_actions()
        
    def setup_actions(self):
        """Configure all element actions"""
        self.query_btn.on_finished_edit = self.load_query_type
        self.weeks_btn.on_press = self.weeks_press
        self.Yaxis_weight_btn.on_press = self.weight_btn_press
        self.Yaxis_reps_btn.on_press = self.reps_btn_press
        self.Yaxis_volume_btn.on_press = self.volume_btn_press

    def load_query_type(self):
        selected_query = self.query_btn.getSelectedOption()
        # check if muscle group was selected, if so, need to ask for a specifice excercise in a form
        if selected_query == "weight":
            self.query = "weight"
            self.queryAxisY = "weight"
            #print("weight query selected")
            self.plotter.change_plot_color(StyleManager.current_style.text_color)
            self.set_plotter_data()
            # Deactivate Reps and Volume buttons and activate KG
            self.Yaxis_reps_btn.selectable = False
            self.Yaxis_volume_btn.selectable = False
            self.Yaxis_weight_btn.activate()
            # Redo neighbors
            # Reconnect queryTypePanel and queryAxisPanel
            for type_btn in self.queryTypePanel.getElements():
                type_btn.set_neighbor("up", self.queryAxisPanel.getSelectableElements()[-1])
            self.queryAxisPanel.getSelectableElements()[0].set_neighbor("down", self.queryTypePanel.getElements()[0])
            #print(self.queryTypePanel.getElements()[0])

            
        elif selected_query in self.manager.queryTool.get_all_targets():
            # Form
            form = FormGetExerciseOptions(screen=self.screen,manager=self.manager, return_menu_instance=self, selected_query=selected_query)
            self.manager.create_form(form,self)
                    
        else:
            print(f"Selected query: {selected_query} is unhandeled.")

    
    def weeks_press(self):
        self.manager.create_form(self.week_input_form,self)

    def update_weeks(self):
        self.weeks_btn.text = f"{self.week_input_form.getValue()} Weeks"
        # update query with new date values
        self.set_plotter_data()
        
    def update_ploter_on_edit_finished(self,selected_query):
        #print(self.query)
        self.queryAxisY = "weight" # Default Y axis value
        self.plotter.y_label = self.queryAxisY
        self.Yaxis_weight_btn.activate()
        self.Yaxis_reps_btn.deactivate()
        self.Yaxis_volume_btn.deactivate()
        self.plotter.change_plot_color(StyleManager.get_muscle_group_color(selected_query)["bg_color"])
        self.set_plotter_data()
        # Activate Reps and Volume buttons
        self.Yaxis_reps_btn.selectable = True
        self.Yaxis_volume_btn.selectable = True
        # Redo neighbors
        # Reconnect queryTypePanel and queryAxisPanel
        for type_btn in self.queryTypePanel.getElements():
            type_btn.set_neighbor("up", self.queryAxisPanel.getSelectableElements()[-1])
        self.queryAxisPanel.getSelectableElements()[-1].set_neighbor("down", self.queryTypePanel.getElements()[0])

        self.queryTypePanel.setNeighbors()
        self.queryAxisPanel.setNeighbors()

    def set_initial_focus_on_switch(self):
        # Set focus to the first nav bar button or any default element
        self.set_initial_focus(self.nav_bar.buttons[3])
        self.nav_bar.buttons[3].activate()

    def set_plotter_data(self):
        # Set plotter data, from the context of Menu make query to database and update x_vals and y_vals
        if self.query == "weight":
            self.y_vals, self.x_vals = self.manager.queryTool.get_bodyweight_history(self.week_input_form.getValue())
            self.x_vals.reverse()
            self.y_vals.reverse()
            #print(f"Y values: {self.y_vals}, X values: {self.x_vals}")
        else:
            self.y_vals, self.x_vals = self.manager.queryTool.get_exercise_history(self.query, self.week_input_form.getValue())
            self.y_vals = [entry[self.queryAxisY] for entry in self.y_vals]
            self.x_vals.reverse()
            self.y_vals.reverse()
            #print(f"Y values: {self.y_vals}, X values: {self.x_vals}")
        self.plotter.update_data(x_values=self.x_vals, y_values=self.y_vals)

    def weight_btn_press(self):
        self.Yaxis_weight_btn.activate()
        self.Yaxis_reps_btn.deactivate()
        self.Yaxis_volume_btn.deactivate()
        self.queryAxisY = "weight"
        self.plotter.y_label = self.queryAxisY
        self.set_plotter_data()
    def reps_btn_press(self):
        self.Yaxis_weight_btn.deactivate()
        self.Yaxis_reps_btn.activate()
        self.Yaxis_volume_btn.deactivate()
        self.queryAxisY = "reps"
        self.plotter.y_label = self.queryAxisY
        self.set_plotter_data()
    def volume_btn_press(self):
        self.Yaxis_weight_btn.deactivate()
        self.Yaxis_reps_btn.deactivate()
        self.Yaxis_volume_btn.activate()
        self.queryAxisY = "volume"
        self.plotter.y_label = self.queryAxisY
        self.set_plotter_data()

