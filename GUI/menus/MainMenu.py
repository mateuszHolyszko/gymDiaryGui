import pygame
from GUI.Menu import Menu
from GUI.Panel import Panel
from GUI.panels.navigation_bar import NavigationBar
from GUI.elements.Button import Button
from GUI.elements.ValueDisplay import ValueDisplay
from GUI.elements.Image.Image2D import Image2D
from GUI.elements.Label import Label
from GUI.elements.InputField import InputField
from GUI.elements.Image.Image2D_Graph import Image2D_Graph
from GUI.elements.Image.ImageCarousel import ImageCarousel
from GUI.style import StyleManager


class MainMenu(Menu):
    def setup(self):
        """Setup panels, elements and actions"""
        screenWidth, screenHeight = pygame.display.get_surface().get_size() # Get screen size

        # Add navigation bar
        self.nav_bar = self.add_panel(NavigationBar)
        
        # Create InputPanel panel
        height = (screenHeight - self.nav_bar.height)//2
        self.LabelPanel = self.add_panel(Panel, x=50, y=(screenHeight - self.nav_bar.height)//2, width=screenWidth//4, height=height)
        self.InputPanel = self.add_panel(Panel, x=50, y=(screenHeight - self.nav_bar.height)//2 + 50, width=screenWidth//4, height=height,layout_type="horizontal")
        # Volume summary panel gets created after the CarouselPanel gets initiated, since its depended on CarouselPanel elements
        # Create CarouselPanel panel
        self.CarouselPanel = self.add_panel(Panel,x=screenWidth//1.7,y=25,width=screenWidth//2 - 5,height=screenHeight - self.nav_bar.height - 10)
        
        # MetaDataDisplay panel
        # Load metadata
        meta = self._load_project_meta()
        print(meta)
        self.MetaDataDisplayPanel = self.add_panel(Panel, x=50, y=(screenHeight - self.nav_bar.height)//2 - 80 , width=screenWidth//4, height=height)
        self.metaDisplay = ValueDisplay(prompt="Project data", 
            value=
              f"Ver: {meta['Version']}: {meta['VersionData']}\n"
              f"Status: {meta['Status']}\n"
              f"Author: {meta['Author']}",
              height=125,
              width=150)
        self.MetaDataDisplayPanel.add_element(self.metaDisplay)

        # Logo
        self.logoPanel = self.add_panel(Panel, x=self.MetaDataDisplayPanel.x, y=-20 , width=self.MetaDataDisplayPanel.width, height=self.MetaDataDisplayPanel.height)
        self.logo = Image2D(image_path="GUI\elements\Image\images\\Logo.png", height = 474//3 , width= 424//3, manager=self.manager,layer=2)
        self.logoPanel.add_element(self.logo)

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
                last_bodyweight = self.manager.queryTool.get_last_bodyweight()
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
        self.inputField = InputField(bodyweight, min_value=0, max_value=150, step=0.1, manager=self.manager)
        self.btn = Button("+", self.inputField.height, self.inputField.height, manager=self.manager)
        self.label = Label(text="Update bodyweight", width=200, height=50, manager=self.manager)
        
        self.LabelPanel.add_element(self.label)
        self.InputPanel.add_element(self.inputField)
        self.InputPanel.add_element(self.btn)

        # Add elements (Carousel panel)
        self.image1 = Image2D_Graph(image_path="GUI\elements\Image\images\\Front.png", height = 290 , width= 300*0.7, manager=self.manager,layer=2)
        self.image1.muscleGroups = ["Forearms", "Biceps", "Triceps","Shoulders","Chest","Back","Abs","Quads","Calves"]
        self.image2 = Image2D_Graph(image_path="GUI\elements\Image\images\\Back.png", height = 280 , width= 300*0.5, manager=self.manager,layer=2)
        self.image2.muscleGroups = ["Back","Shoulders","Triceps","Forearms","Glutes","Hamstrings","Calves"]
        self.imageImageCarousel = ImageCarousel(images=[], manager=self.manager, mode="random_timed", height = 300 , width= 300*0.7,layer=2)
        self.CarouselPanel.add_element(self.imageImageCarousel)
        self.imageImageCarousel.add_image(self.image1)
        self.imageImageCarousel.add_image(self.image2)

        # Create volumeSummary panel
        self.volumeSummary = self.add_panel(Panel, x=self.imageImageCarousel.x - 200, y=self.imageImageCarousel.y,width=screenWidth//4, height=self.imageImageCarousel.height)
        self.update_carousel()

        # Create volumeLabel panel
        self.volumeLabelPanel = self.add_panel(Panel, x=self.volumeSummary.x, y=self.imageImageCarousel.y-55,width=screenWidth//2, height=50)
        self.volumeLabel = Label(text="Volume summary of 3 weeks", width=200, height=50, manager=self.manager)
        self.volumeLabelPanel.add_element(self.volumeLabel)
        
        # Connect navigation between nav bar and InputPanel
        for nav_btn in self.nav_bar.buttons:
            nav_btn.set_neighbor("up", self.InputPanel.getElements()[-1])  # Last element in InputPanel
        for btn in self.InputPanel.getSelectableElements():
            btn.set_neighbor("down", self.nav_bar.buttons[0])
        self.nav_bar.buttons[0].activate()

        # Connect navigation between InputPanel and table
        for InputPanel_btn in self.InputPanel.getElements():
            InputPanel_btn.set_neighbor("right", self.CarouselPanel.getElements()[0])  # First element in table
        self.CarouselPanel.getElements()[0].set_neighbor("left", self.InputPanel.getElements()[1])

        # Connect neighbors within (can be done via panel or manualy)
        self.InputPanel.setNeighbors()
        self.CarouselPanel.setNeighbors()
        
        # Set up actions
        self.setup_actions()
        
    def setup_actions(self):
        """Configure all element actions"""
        self.inputField.on_press = lambda: print(f"Selected value is {self.inputField.value}")
        self.btn.on_press = self.updateBodyWeight
        self.imageImageCarousel.update = self.update_carousel
        
        
    def updateBodyWeight(self):
        self.manager.context["bodyweight"] = self.inputField.value
        self.manager.notification_system.show(f"Bodyweight updated to {self.inputField.value} kg", 3)

    def update_carousel(self):
        # Delete existing elements in volumeSummary panel
        #print("Update carousel")
        self.volumeSummary.clear_elements()
        # Add elements (volumeSummary panel)
        for targetMuscle in self.imageImageCarousel.get_image().muscleGroups:
            btn = Button(text=f"{targetMuscle}: {self.manager.queryTool.get_muscle_workload(muscle=targetMuscle,weeks=3)["total_sets"]}", width=150, height=30, manager=self.manager)
            btn.set_style_override({'bg_color': StyleManager.get_muscle_group_color(targetMuscle)['bg_color']})
            self.volumeSummary.add_element(btn)

    def set_initial_focus_on_switch(self):
        # Set focus to the first nav bar button or any default element
        self.set_initial_focus(self.nav_bar.buttons[0])

    def _load_project_meta(self):
        """Load project metadata from project_meta.txt in parent directory"""
        meta = {}
        try:
            # Go up one directory and read the file
            with open("project_meta.txt", "r") as f:
                for line in f.readlines():
                    if ":" in line:
                        key, value = line.strip().split(":", 1)
                        meta[key.strip()] = value.strip().rstrip(",")
        except FileNotFoundError:
            print("Warning: project_meta.txt not found")
            meta = {
                "VersionData": "Unknown",
                "Version": "Unknown",
                "Branch": "Unknown",
                "Status": "Unknown",
                "Author": "Unknown"
            }
        return meta
        