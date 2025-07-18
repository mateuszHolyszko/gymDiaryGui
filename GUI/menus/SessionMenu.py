from GUI.Menu import Menu
from GUI.Panel import Panel
from GUI.panels.navigation_bar import NavigationBar
from GUI.elements.Button import Button

class SessionMenu(Menu):
    def setup(self):
        """Setup panels, elements and actions"""
        # Add navigation bar
        self.nav_bar = self.add_panel(NavigationBar)
        
        # Create content panel
        self.content = self.add_panel(Panel, 50, 50, 700, 400)
        
        # Add elements
        self.start_btn = Button("TestSesion1", width=200, height=50, manager=self.manager)
        self.settings_btn = Button("TestSesion2", width=200, height=50, manager=self.manager)
        
        self.content.add_element(self.start_btn)
        self.content.add_element(self.settings_btn)
        
        # Connect navigation between nav bar and content
        for nav_btn in self.nav_bar.buttons:
            nav_btn.set_neighbor("up", self.settings_btn)
        self.content.getElements()[-1].set_neighbor("down", self.nav_bar.buttons[1])
        self.nav_bar.buttons[1].activate()

        self.start_btn.set_neighbor("down", self.settings_btn)
        self.settings_btn.set_neighbor("up", self.start_btn)
        
        # Set initial focus through manager
        self.set_initial_focus(self.nav_bar.buttons[1])  # Focus on Session button
        
        # Set up actions
        self.setup_actions()
        
    def setup_actions(self):
        """Configure all element actions"""
        self.start_btn.on_press = self.start_workout
        self.settings_btn.on_press = self.open_settings
        
    def start_workout(self):
        print("Starting workout...")
        self.manager.switch_to("SessionMenu")
        
    def open_settings(self):
        print("Opening settings...")
        # Could switch to settings menu here