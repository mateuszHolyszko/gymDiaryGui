import pygame
import random
import time
from GUI.Menu import Menu
from GUI.Panel import Panel
from GUI.elements.Button import Button
from datetime import datetime
from GUI.elements.Display3D import Display3D
from GUI.menus.MainMenu import MainMenu
from GUI.menus.SessionMenu import SessionMenu
from GUI.menus.ProgramMenu import ProgramMenu
from GUI.menus.StatsMenu import StatsMenu
from GUI.elements.LoadingConsole import LoadingConsole

class MockLoadingMenu(Menu):
    def setup(self):
        """Setup panels, elements and actions"""
        screenWidth, screenHeight = pygame.display.get_surface().get_size() # Get screen size
        self.update = lambda dt : None  # Update by defult does nothing

        self.buttonsPanel = Panel(x=0,y=screenHeight-60,width=screenWidth,height=60,manager=self.manager,layout_type="horizontal")

        self.exerciseModuleBtn = Button(x=0,y=0,width=screenWidth//6,height=self.buttonsPanel.height - 10,text="Exercise Module",manager=self.manager)
        self.buttonsPanel.add_element(self.exerciseModuleBtn)
        self.wipModule1 = Button(x=0,y=0,width=screenWidth//6,height=self.buttonsPanel.height - 10,text="Wip Module 1",manager=self.manager)
        self.wipModule2 = Button(x=0,y=0,width=screenWidth//6,height=self.buttonsPanel.height - 10,text="Wip Module 2",manager=self.manager)
        self.buttonsPanel.add_element(self.wipModule1)
        self.wipModule1.deactivate()
        self.wipModule1.selectable = False
        self.buttonsPanel.add_element(self.wipModule2)
        self.wipModule2.deactivate()
        self.wipModule2.selectable = False

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
        self.console = LoadingConsole(x=0,y=0,width=self.consolePanel.width,height=self.consolePanel.height,manager=self.manager)
        self.consolePanel.add_element(self.console)
        self.console.printText("- Choose module to load: ")
        self.console._advance_row()


        self.add_panel_instance(self.panel3D)
        self.add_panel_instance(self.consolePanel)
        self.add_panel_instance(self.buttonsPanel)
        
        self.connectNeighbors()
        
        # Set up actions
        self.setup_actions()

        # Stores actual steps in loading (classes that will be instantiated)
        self.ExerciseModuleLoading_steps = [
            ("MainMenu", MainMenu),
            ("SessionMenu", SessionMenu),
            ("ProgramMenu", ProgramMenu),
            ("StatsMenu", StatsMenu)
        ]

        self.current_step = 0
        self.previous_time = time.time()
        self.next_delay = random.uniform(0.5, 1.5)  # random time interval for step


    def setup_actions(self):
        """Configure all element actions"""
        self.exerciseModuleBtn.on_press = self.exerciseModuleAction
        

    def connectNeighbors(self):
        pass

    def exerciseModuleAction(self):
        # Start mock loading (menus will load gradually in update loop)
        self.update = self.loadUpdate
        self.current_step = 0
        self.start_load_time = time.time()
        self.delays = []
        for i in range(1,18): #4loading bars, for each 3giberish lines
            if i%4 == 1:
                self.delays.append(random.uniform(0.5, 1.5))
            else:
                self.delays.append(random.uniform(0.2, 0.6))
        #print(self.next_delays)
        self.queue_iterator=0
        self.printed_flag = False


    def loadUpdate(self, dt):
        """Called every frame, dt = delta time in seconds"""
        # this will replace usual Menu update which gets called each frame with delta time
        if self.queue_iterator >= len(self.delays)-1:
            # when finished
            self.exerciseModuleBtn.activate()
            self.exerciseModuleBtn.on_press = self.switch_to_exercise_module
            self.console._advance_row()
            self.console.printText("    ===  Exercise Module loaded  ===")
            # revert the menu.update function to do nothing, so that this case is not processed
            self.update = lambda dt : None
        elif self.queue_iterator % 4 == 0:
            #ProgressBar
            prog = min((time.time() - self.start_load_time)/self.delays[self.queue_iterator] , 1)
            name, cls = self.ExerciseModuleLoading_steps[self.queue_iterator//4]
            menu_instance = cls(self.manager.gui_surface, self.manager)
            self.manager.register_menu(name, menu_instance)
            self.console.drawProgressBar(prompt=f"  Loading menu -> {self.ExerciseModuleLoading_steps[self.queue_iterator//4][0]}   ({self.queue_iterator//4+1}/{len(self.ExerciseModuleLoading_steps)})",startingCol=0,progress=prog)
            if prog >= 1:
                #Gen Gib list that will be used for next 3
                self.gibList = self.console.getGiberishList()
                self.queue_iterator += 1
                self.start_load_time = time.time()
                self.console._advance_row()
                self.console._advance_row()
                self.console._advance_row()
            
        elif self.queue_iterator < len(self.delays):
            prog = min((time.time() - self.start_load_time)/self.delays[self.queue_iterator] , 1)
            #Giberish line
            if self.printed_flag == False:
                self.console.printText(self.gibList[self.queue_iterator%4 - 1])
                self.console._advance_row()
                self.printed_flag = True
            if prog >= 1:
                self.printed_flag = False
                self.gibList = self.console.getGiberishList()
                self.queue_iterator += 1
                self.start_load_time = time.time()    
            

    def loadUpdatee(self, dt):
        """Called every frame, dt = delta time in seconds"""
        # this will replace usual Menu update which gets called each frame with delta time
        # If we're in loading mode
        if self.current_step < len(self.ExerciseModuleLoading_steps):
            now = time.time()
            #print(f"step: {((now - self.previous_time)/self.next_delay):.2f}%")
            # when it steps over boundary and is yet to be checked it will be >100% so cap it
            prog = min((now - self.previous_time)/self.next_delay , 1)
            self.console.drawProgressBar(prompt=f"  Loading menu -> {self.ExerciseModuleLoading_steps[self.current_step][0]}   ({self.current_step+1}/{len(self.ExerciseModuleLoading_steps)})",startingCol=0,progress=prog)
            if now - self.previous_time >= self.next_delay:
                # Load current menu
                name, cls = self.ExerciseModuleLoading_steps[self.current_step]
                menu_instance = cls(self.manager.gui_surface, self.manager)
                self.manager.register_menu(name, menu_instance)
                #progress console row
                self.console._advance_row()
                self.console._advance_row()
                self.console._advance_row()
                
                gibList = self.console.getGiberishList()
                for nonsense in gibList:
                    self.console.printText(nonsense)
                    self.console._advance_row()
                self.console._advance_row()
                #print(f"loaded {name}")
                #print(f"progress: {self.current_step+1}/{len(self.ExerciseModuleLoading_steps)}")

                self.current_step += 1
                self.previous_time = now
                self.next_delay = random.uniform(0.5, 1.5)
                

            # when finished
            if self.current_step == len(self.ExerciseModuleLoading_steps):
                self.exerciseModuleBtn.activate()
                self.exerciseModuleBtn.on_press = self.switch_to_exercise_module
            
                

    def switch_to_exercise_module(self):
        self.manager.switch_to("MainMenu")
        self.display_3d.release()

    def set_initial_focus_on_switch(self):
        # Set focus to the first nav bar button or any default element
        self.set_initial_focus(self.buttonsPanel.getElements()[0])
