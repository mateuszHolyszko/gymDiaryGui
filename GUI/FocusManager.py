class FocusManager:
    def __init__(self):
        self.current_focus = None
        self.focus_history = []

    def set_focus(self, element):
        """Set focus to a new element"""
        if self.current_focus:
            self.current_focus.is_focused = False
            self.focus_history.append(self.current_focus)
        
        self.current_focus = element
        if element:
            element.is_focused = True

    def restore_previous_focus(self):
        """Return to the last focused element"""
        if self.focus_history:
            previous = self.focus_history.pop()
            self.set_focus(previous)
            return True
        return False

    def clear_focus(self):
        """Clear all focus states"""
        if self.current_focus:
            self.current_focus.is_focused = False
        self.current_focus = None
        self.focus_history = []