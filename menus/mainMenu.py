from elements.panel import Panel
from elements.button import Button
from elements.label import Label
from elements.inputField import InputField
from elements.InputSelect import InputSelect
from elements.pane3D import Pane3D
from elements.misc.clock import Clock


def main_menu_controller(window_manager):
    # Main window panel (vertical layout, fills the screen)
    main_window = Panel("main_window", x=0, y=0, width=820, height=480, layout_type="vertical",draw_box=False)

    # Panel 1: Navigation buttons (horizontal layout)
    panel1 = Panel("panel1", x=0, y=0, width=820, height=100, layout_type="horizontal")
    btn1 = Button("btn1", "Go to Main Menu", x=0, y=0, width=160, height=80,selectable=False, on_press=lambda: print("Switch to Window A (placeholder)"))
    btn2 = Button("btn2", "Go to Table Menu", x=0, y=0, width=160, height=80, on_press=lambda: window_manager.handle_action("switch_menu", menu="table"))
    btn3 = Button("btn3", "Go to Window C", x=0, y=0, width=160, height=80, on_press=lambda: print("Switch to Window C (placeholder)"))
    btn4 = Button("btn4", "Go to Window D", x=0, y=0, width=160, height=80, on_press=lambda: print("Switch to Window D (placeholder)"))
    clock = Clock("main_clock", width=160, height=80,time_format="%H:%M:%S")  # Shows seconds toodate_format="%A, %B %d %Y"  # E.g. "Monday, January 01 2023"
    
    panel1.add_child(btn1)
    panel1.add_child(btn2)
    panel1.add_child(btn3)
    panel1.add_child(btn4)
    panel1.add_child(clock)

    # Panel 2: Labels (vertical layout)
    panel2 = Panel("panel2", x=0, y=110, width=400, height=260, layout_type="vertical")
    label1 = Label("label1", "Label 1", x=0, y=0, width=380, height=30, selectable=False)
    label2 = Label("label2", "Label 2", x=0, y=0, width=380, height=30, selectable=True)
    label3 = Label("label3", "Label 3", x=0, y=0, width=380, height=30, selectable=False)

    # InputField that updates label1 on ENTER
    input_field = InputField("input1", x=0, y=0, width=380, height=30)

    def on_input_finished(value):
        window_manager.handle_action("update_label", label_elem=label1, text=value)
        print(f"Label1 updated to: {value}")

    input_field.connect("editing_finished", on_input_finished)

    panel2.add_child(label1)
    panel2.add_child(label2)
    panel2.add_child(label3)
    panel2.add_child(input_field)

    options = ["Option A", "Option B", "Option C"]
    input_select = InputSelect("input_select_example", options, x=0, y=0, width=380, height=30, window_manager=window_manager)
    panel2.add_child(input_select)

    # Panel 3: Exit and placeholder button (horizontal layout)
    panel3 = Panel("panel3", x=0, y=380, width=400, height=100, layout_type="horizontal")
    exit_btn = Button("exit_btn", "Exit", x=0, y=0, width=180, height=80, on_press=lambda: window_manager.handle_action("exit"))
    placeholder_btn = Button("placeholder_btn", "Placeholder", x=0, y=0, width=180, height=80, on_press=lambda: print("Placeholder action"))
    panel3.add_child(exit_btn)
    panel3.add_child(placeholder_btn)

    # Pane3D for 3D model rendering (placeholder)
    panel4 = Panel("panel4", x=405, y=110, width=400, height=370, layout_type="vertical", selectable=False, draw_box=True)
    pane3d = Pane3D("model_view", "Renderer3D\models\male_003.fbx.stl",width=395, height=365, selectable=False)
    panel4.add_child(pane3d)

    # Assemble main window (panels arranged vertically)
    main_window.add_child(panel1)
    main_window.add_child(panel2)
    main_window.add_child(panel3)
    main_window.add_child(panel4)

    return main_window, btn2  # Start focus on first button