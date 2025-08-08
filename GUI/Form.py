from GUI.Menu import Menu

class Form(Menu):
    def __init__(self, screen, manager, return_menu_instance=None):
        super().__init__(screen, manager)
        self.return_menu_instance = return_menu_instance

    def exit(self):
        """Switch back to the return menu instance."""
        if self.return_menu_instance is not None:
            self.manager.focus_manager.clear_focus()
            # If not found by instance, fallback to first menu
            self.manager.current_menu = self.return_menu_instance
            if hasattr(self.return_menu_instance, "set_initial_focus_on_switch"):
                self.return_menu_instance.set_initial_focus_on_switch()