import pygame
from GUI.Menu import Menu
from GUI.Panel import Panel
from GUI.ScrollingTableVertical import ScrollingTableVertical
from GUI.panels.navigation_bar import NavigationBar
from GUI.elements.Button import Button
from GUI.elements.SelectDropDown import SelectDropDown
from datetime import datetime
from GUI.menus.FormYesNo import FormYesNo
from GUI.elements.Display3D import Display3D

class MockLoadingMenu(Menu):
    def setup(self):
        """Setup panels, elements and actions"""
        screenWidth, screenHeight = pygame.display.get_surface().get_size() # Get screen size

        self.buttonsPanel = Panel(x=0,y=screenHeight-80,width=screenWidth,height=80,manager=self.manager)

        self.mainMenuBtn = Button(x=0,y=0,width=screenWidth//6,height=self.buttonsPanel.height - 10,text="START",manager=self.manager)
        self.buttonsPanel.add_element(self.mainMenuBtn)

        self.panel3D = Panel(x=0,y=0,width=screenWidth*0.4,height=screenHeight-self.buttonsPanel.height,manager=self.manager)

        self.display_3d = Display3D(
            x=0, y=0, width=self.panel3D.width, height=self.panel3D.height,
            manager=self.manager,
            ctx=self.manager.screen3Drefs['ctx'],
            fbo_3d=self.manager.screen3Drefs['fbo'],
            tex_3d=self.manager.screen3Drefs['tex'],
            model_path="GUI\ThreeDee\models\Mat.obj",
            vertex_shader_path="GUI\ThreeDee\shaders\\basic.vert",
            fragment_shader_path="GUI\ThreeDee\shaders\\basic.frag",
            target_size=2
        )
        self.panel3D.add_element(self.display_3d)

        self.consolePanel = Panel(x=self.panel3D.width,y=0,width=screenWidth-self.panel3D.width,height=screenHeight-self.buttonsPanel.height,manager=self.manager)


        self.add_panel_instance(self.panel3D)
        self.add_panel_instance(self.consolePanel)
        self.add_panel_instance(self.buttonsPanel)
        
        self.connectNeighbors()
        
        # Set up actions
        self.setup_actions()
        
    def setup_actions(self):
        """Configure all element actions"""
        self.mainMenuBtn.on_press = self.go_to_main_menu
        

    def connectNeighbors(self):
        pass

    def go_to_main_menu(self):
        self.manager.switch_to("MainMenu")
        # release model res
        self.display_3d.release()

    def set_initial_focus_on_switch(self):
        # Set focus to the first nav bar button or any default element
        self.set_initial_focus(self.buttonsPanel.getElements()[0])