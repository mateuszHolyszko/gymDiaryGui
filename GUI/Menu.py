from GUI.Panel import Panel
from GUI.Table import Table
from GUI.panels.navigation_bar import NavigationBar
class Menu:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.panels = []
        self.setup()  # Automatically call setup during initialization
        
    def setup(self):
        """Override this to:
        1. Add panels
        2. Create elements
        3. Set up actions
        """
        pass
        
    def add_panel(self, panel_class, *args, **kwargs):
        """Add a panel by class reference and return it"""
        # Ensure manager is passed but not duplicated
        if 'manager' not in kwargs:
            kwargs['manager'] = self.manager
        panel = panel_class(*args, **kwargs)
        self.panels.append(panel)
        return panel
    
    def add_panel_instance(self, panel_instance):
        """Add an existing panel instance to the menu"""
        if isinstance(panel_instance, (Panel,Table,NavigationBar)):
            self.panels.append(panel_instance)
        else:
            raise TypeError("Expected a Panel instance")
    
    def remove_panel(self, panel):
        """Remove a panel from the menu"""
        if panel in self.panels:
            self.panels.remove(panel)
    
    def remove_panels(self,except_panels=None):
        """Remove all panels except specified ones"""
        if except_panels is None:
            except_panels = []
        for panel in self.panels[:]:
            if panel not in except_panels:
                self.remove_panel(panel)

        
    def render(self, screen):
        # Collect all elements from all panels with their layer and panel info
        all_elements = []
        for panel in self.panels:
            for element in panel.elements:
                all_elements.append((element.layer, element))
    
        # Sort all elements by layer and render them
        for layer, element in sorted(all_elements, key=lambda x: x[0]):
            element.render(screen)

    def set_initial_focus(self, element):
        """Delegate to manager's focus system"""
        self.manager.focus_manager.set_focus(element)
            
    def handle_event(self, event):
        """Delegate event handling to manager"""
        return self.manager.handle_event(event)