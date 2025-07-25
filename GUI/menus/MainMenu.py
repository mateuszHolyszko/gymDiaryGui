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
from workout_db.sessions_db import SessionsDB
from GUI.elements.SessionCell import SessionCell
from GUI.elements.Image.Image2D import Image2D
from GUI.elements.Image.ImageCarousel import ImageCarousel


class MainMenu(Menu):
    def setup(self):
        self.database = ProgramsDB()
        self.session = SessionsDB()
        """Setup panels, elements and actions"""
        screenWidth, screenHeight = pygame.display.get_surface().get_size() # Get screen size

        # Add navigation bar
        self.nav_bar = self.add_panel(NavigationBar)
        
        # Create content panel
        self.content = self.add_panel(Panel, x=0, y=0, width=screenWidth//2, height=screenHeight - self.nav_bar.height)
        # Create second panel
        self.content2 = self.add_panel(Panel,x=screenWidth//2,y=5,width=screenWidth//2 - 5,height=screenHeight - self.nav_bar.height - 10)
        
        # Add elements (content panel)
        bodyweight = None
        # get bodyweight from main menu context, if its not there get it from last session
        try:
            bodyweight = self.manager.context["bodyweight"]
            if bodyweight is None:
                raise KeyError("Bodyweight is None")  # Force fallback to last session
            print(bodyweight)
        except (KeyError, AttributeError) as e:
            # Fallback 1: Try getting bodyweight from last session
            try:
                last_bodyweight = self.session.get_last_bodyweight()
                if last_bodyweight is not None:
                    bodyweight = last_bodyweight
                    if bodyweight is not None:
                        print(bodyweight)
                        self.manager.context["bodyweight"] = bodyweight
                    else:
                        print("Warning: Bodyweight not found in last session")
                else:
                    print("Warning: No sessions available")
            except Exception as e:
                print(f"Error retrieving last session: {str(e)}")
        self.inputField = InputField(bodyweight, min_value=0, max_value=150, step=0.25, manager=self.manager)
        self.btn = Button("Update bodyweight", width=200, height=50, manager=self.manager)
        self.label = Label(text="Label", width=200, height=50, manager=self.manager)
        
        self.content.add_element(self.label)
        self.content.add_element(self.inputField)
        self.content.add_element(self.btn)

        # Add elements (second panel)
        #self.image = Image2D(image_path="GUI\elements\Image\images\\test1.jpg", width=200, height=200, manager=self.manager)
        self.imageImageCarousel = ImageCarousel(folder_path="GUI\elements\Image\images\\", width=200, height=200, manager=self.manager, mode="selectable")

        #self.content2.add_element(self.image)
        self.content2.add_element(self.imageImageCarousel)
        
        # Connect navigation between nav bar and content
        for nav_btn in self.nav_bar.buttons:
            nav_btn.set_neighbor("up", self.content.getElements()[-1])  # Last element in content
        self.content.getElements()[-1].set_neighbor("down", self.nav_bar.buttons[0])
        self.nav_bar.buttons[0].activate()

        # Connect navigation between content and table
        for content_btn in self.content.getElements():
            content_btn.set_neighbor("right", self.content2.getElements()[0])  # First element in table
        self.content2.getElements()[0].set_neighbor("left", self.content.getElements()[1])

        # Connect neighbors within (can be done via panel or manualy)
        self.content.setNeighbors()
        self.content2.setNeighbors()
        
        # Set initial focus through manager
        self.set_initial_focus(self.nav_bar.buttons[0])
        
        # Set up actions
        self.setup_actions()
        
    def setup_actions(self):
        """Configure all element actions"""
        self.inputField.on_press = lambda: print(f"Selected value is {self.inputField.value}")
        self.btn.on_press = self.updateBodyWeight
        
        
    def updateBodyWeight(self):
        self.manager.context["bodyweight"] = self.inputField.value
        