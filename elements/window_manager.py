class WindowManager:
    def __init__(self, root):
        self.root = root
        self.context = {}

    def handle_action(self, action_name, **kwargs):
        if action_name == "update_label":
            label_elem = kwargs["label_elem"]
            label_elem.text = kwargs["text"]  
        elif action_name == "store_value":
            self.context[kwargs["key"]] = kwargs["value"]
        elif action_name == "exit":
            import sys
            print("Exiting via WindowManager.")
            sys.exit(0)
        elif action_name == "switch_menu":
            menu = kwargs.get("menu")
            if menu == "main":
                from menus.mainMenu import main_menu_controller
                root, first_focus = main_menu_controller(self)
                self.root.children.clear()
                self.root.add_child(root)
                self.context["current_focus"] = first_focus
            elif menu == "table":
                from menus.tableMenu import table_menu_controller
                root, first_focus = table_menu_controller(self)
                self.root.children.clear()
                self.root.add_child(root)
                self.context["current_focus"] = first_focus
        # Add more actions as needed

    def store_value(self, key, value):
        self.context[key] = value

    def get_value(self, key):
        return self.context.get(key)