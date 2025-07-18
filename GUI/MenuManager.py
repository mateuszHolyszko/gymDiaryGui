from GUI.FocusManager import FocusManager

class MenuManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_menu = None
        self.focus_manager = FocusManager()  # Central focus control
        self.menus = {}

    def register_menu(self, name, menu_class):
        self.menus[name] = menu_class

    def switch_to(self, menu_name):
        if menu_name in self.menus:
            self.focus_manager.clear_focus()
            self.current_menu = self.menus[menu_name](self.screen, self)
            return True
        return False

    def handle_event(self, event):
        if not self.current_menu:
            return False

        # Let focused element handle event first
        if self.focus_manager.current_focus and \
           hasattr(self.focus_manager.current_focus, 'handle_event'):
            return self.focus_manager.current_focus.handle_event(event)
        
        return False