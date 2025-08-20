from GUI.FocusManager import FocusManager

class MenuManager:
    def __init__(self, gui_surface,queryTool, notification_system,ctx,fbo,tex):
        self.gui_surface = gui_surface
        self.queryTool = queryTool
        self.notification_system = notification_system
        self.current_menu = None
        self.focus_manager = FocusManager()  # Central focus control
        self.menus = {}
        self.context = {} # for some globalcontext
        self.screen3Drefs = {'ctx':ctx,'fbo':fbo,'tex':tex}

    def register_menu(self, name, menu_instance):
        self.menus[name] = menu_instance

    def switch_to(self, menu_name):
        if menu_name in self.menus:
            self.focus_manager.clear_focus()
            self.current_menu = self.menus[menu_name]
            # Set initial focus for the new menu
            if hasattr(self.current_menu, "set_initial_focus_on_switch"):
                self.current_menu.set_initial_focus_on_switch()
            return True
        return False
    
    def create_form(self, formInstance, returnMenuInstance):
        formInstance.return_menu_instance = returnMenuInstance
        self.focus_manager.clear_focus()
        self.current_menu = formInstance
        if hasattr(self.current_menu, "set_initial_focus_on_switch"):
            self.current_menu.set_initial_focus_on_switch()
        return True

    def handle_event(self, event):
        if not self.current_menu:
            return False

        # Let focused element handle event first
        if self.focus_manager.current_focus and \
           hasattr(self.focus_manager.current_focus, 'handle_event'):          
            hasHappend=self.focus_manager.current_focus.handle_event(event) # first let element consume event
            if hasattr(self.focus_manager.current_focus.parent_panel,'handle_event') and hasHappend==False: # if element didnt consume event, pass it to parent container
                return self.focus_manager.current_focus.parent_panel.handle_event(event)
            else:
                return False
        
        return False