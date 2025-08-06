import pygame
from workout_db.programs_db import ProgramsDB
from GUI.Menu import Menu
from GUI.Panel import Panel
from GUI.ScrollingTableVertical import ScrollingTableVertical
from GUI.panels.navigation_bar import NavigationBar
from GUI.elements.Button import Button
from GUI.elements.SelectDropDown import SelectDropDown
from GUI.Table import Table
from GUI.elements.SessionCell import SessionCell
from workout_db.sessions_db import SessionsDB
from datetime import datetime

class SessionMenu(Menu):
    def setup(self):
        self.database = ProgramsDB()
        self.session = SessionsDB()
        """Setup panels, elements and actions"""
        screenWidth, screenHeight = pygame.display.get_surface().get_size() # Get screen size

        # Add navigation bar
        self.nav_bar = self.add_panel(NavigationBar)
        
        # Create choose session panel
        self.sessionPanel = self.add_panel(Panel, x=0, y=0, width=screenWidth, height=screenHeight //8, layout_type="horizontal")
        # Create table panel
        table_y = 35
        totalRows = len(self.database.get_exercises_in_program(self.database.get_all_program_names()[0]))
        rowHeight = 100
        windowHeight = screenHeight - self.nav_bar.height - self.sessionPanel.height - 25
        totalHeightOfTable = max(windowHeight, totalRows * rowHeight + table_y)
        self.table = ScrollingTableVertical(x=0,y=table_y,width=screenWidth-20,height=windowHeight,totalHeight=totalHeightOfTable,manager=self.manager,cell_height=rowHeight)
        self.add_panel_instance(self.table)
        self.table.draw_table_lines = False 
        # when init we are coming from navbar so offset self.table.max_offset
        self.table.scroll_offset = self.table.max_offset
        
        # Add elements
        programNames = self.database.get_all_program_names()
        self.selectProgram = SelectDropDown(options=programNames, width=screenWidth//4, height=50, manager=self.manager, layer=3)
        self.saveSessionButton = Button(text="Save Session", width=screenWidth//4, height=50, manager=self.manager, layer=1)
        self.sessionPanel.add_element(self.selectProgram)
        self.sessionPanel.add_element(self.saveSessionButton)

        self.table.load_data_session(programNames[0],self.session.getSessionAsList(programNames[0]),manager=self.manager) # Load initial program data
        
        self.connectNeighbors()
        
        # Set up actions
        self.setup_actions()
        
    def setup_actions(self):
        """Configure all element actions"""
        self.selectProgram.on_finished_edit = self.load_program
        self.saveSessionButton.on_press = self.saveSession

    def load_program(self):
        self.table.load_data_session( self.selectProgram.getSelectedOption() ,self.session.getSessionAsList( self.selectProgram.getSelectedOption() ),manager=self.manager) # Load initial program data 
        totalRows = len(self.database.get_exercises_in_program( self.selectProgram.getSelectedOption() ))
        rowHeight = 100
        totalHeightOfTable = max(self.table.height, totalRows * rowHeight + self.table.y )
        self.table.changeDims(newTotalHeight=totalHeightOfTable)
        self.connectNeighbors()
        print(f"y={self.table.y}, height={self.table.height}, totalHeight={self.table.totalHeight}, lastRowCell y={self.table.getElements()[-1].y},last row cell height={self.table.getElements()[-1].height}")
        #when loading we are coming from top so ofsset 0
        self.table.scroll_offset = 0
        

    def connectNeighbors(self):
         # Connect neighbors within (can be done via panel or manualy)
        self.sessionPanel.setNeighbors()
        self.table.setNeighbors()

        # Connect navigation between nav bar and table
        for nav_btn in self.nav_bar.buttons:
            nav_btn.set_neighbor("up", self.table.getSelectable(-1))  # last element
        for elem in self.table.getElementsInRow(-1):
            elem.set_neighbor("down", self.nav_bar.buttons[1])

        # Connect navigation between table and sessionPanel
        for sessionPanel in self.sessionPanel.getElements():
            sessionPanel.set_neighbor("down", self.table.getSelectable(1))  # First slectable!!! element in table
        for elem in self.table.getElementsInRow(0): # First non header row
            elem.set_neighbor("up", self.selectProgram)

    def saveSession(self):
        bodyweight = self.manager.context["bodyweight"]
        print(bodyweight)
        JSONdata = self.table.get_session_data_JSON(self.selectProgram.getSelectedOption(), datetime.now().strftime("%d-%m-%Y"), bodyweight )
        #print(JSONdata)
        self.manager.context["session_data"] = JSONdata # temporaly storage, so we can access it in Form
        self.manager.switch_to("Form")

    def set_initial_focus_on_switch(self):
        # Set focus to the first nav bar button or any default element
        self.set_initial_focus(self.nav_bar.buttons[1])
        self.nav_bar.buttons[1].activate()