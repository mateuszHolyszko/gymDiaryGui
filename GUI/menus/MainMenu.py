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
from GUI.style import StyleManager


class MainMenu(Menu):
    def setup(self):
        self.database = ProgramsDB()
        self.session = SessionsDB()
        """Setup panels, elements and actions"""
        screenWidth, screenHeight = pygame.display.get_surface().get_size() # Get screen size

        # Add navigation bar
        self.nav_bar = self.add_panel(NavigationBar)
        
        # Create InputPanel panel
        self.InputPanel = self.add_panel(Panel, x=0, y=0, width=screenWidth//4, height=screenHeight - self.nav_bar.height)
        # Volume summary panel gets created after the CarouselPanel gets initiated, since its depended on CarouselPanel elements
        # Create CarouselPanel panel
        self.CarouselPanel = self.add_panel(Panel,x=screenWidth//2,y=5,width=screenWidth//2 - 5,height=screenHeight - self.nav_bar.height - 10)
        
        # Add elements (InputPanel panel)
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
        
        self.InputPanel.add_element(self.label)
        self.InputPanel.add_element(self.inputField)
        self.InputPanel.add_element(self.btn)

        # Add elements (Carousel panel)
        self.image1 = Image2D(image_path="GUI\elements\Image\images\\Front.png", height = 290 , width= 300*0.7, manager=self.manager)
        self.image2 = Image2D(image_path="GUI\elements\Image\images\\Back.png", height = 280 , width= 300*0.5, manager=self.manager)
        self.imageImageCarousel = ImageCarousel(images=[], manager=self.manager, mode="random_timed", height = 300 , width= 300*0.7)
        self.CarouselPanel.add_element(self.imageImageCarousel)
        self.imageImageCarousel.add_image(self.image1)
        self.imageImageCarousel.add_image(self.image2)

        # Create volumeSummary panel
        self.volumeSummary = self.add_panel(Panel, x=self.imageImageCarousel.x - 200, y=self.imageImageCarousel.y,width=screenWidth//4, height=self.imageImageCarousel.height)
        # Add elements (volumeSummary panel)
        for targetMuscle in self.database.get_muscle_groups():
            btn = Button(text=f"{targetMuscle}: (SUM)", width=150, height=30, manager=self.manager)
            btn.set_style_override({'bg_color': StyleManager.get_muscle_group_color(targetMuscle)['bg_color']})
            self.volumeSummary.add_element(btn)
        
        # Connect navigation between nav bar and InputPanel
        for nav_btn in self.nav_bar.buttons:
            nav_btn.set_neighbor("up", self.InputPanel.getElements()[-1])  # Last element in InputPanel
        self.InputPanel.getElements()[-1].set_neighbor("down", self.nav_bar.buttons[0])
        self.nav_bar.buttons[0].activate()

        # Connect navigation between InputPanel and table
        for InputPanel_btn in self.InputPanel.getElements():
            InputPanel_btn.set_neighbor("right", self.CarouselPanel.getElements()[0])  # First element in table
        self.CarouselPanel.getElements()[0].set_neighbor("left", self.InputPanel.getElements()[1])

        # Connect neighbors within (can be done via panel or manualy)
        self.InputPanel.setNeighbors()
        self.CarouselPanel.setNeighbors()
        
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
        