from elements.panel import Panel
from elements.button import Button
from elements.label import Label
from elements.inputField import InputField
from elements.table import Table, Cell
from elements.misc.clock import Clock

from workout_db.programs_db import ProgramsDB

def table_menu_controller(window_manager):

    # Initialize the database
    programs_db = ProgramsDB()

    # Main window panel (vertical layout, fills the screen)
    main_window = Panel("main_window", x=0, y=0, width=820, height=480, layout_type="vertical")

    # Panel 1: Navigation buttons (horizontal layout)
    panel1 = Panel("panel1", x=0, y=0, width=820, height=100, layout_type="horizontal")
    btn1 = Button("btn1", "Go to Main Menu", x=0, y=0, width=160, height=80, on_press=lambda: window_manager.handle_action("switch_menu", menu="main"), selectable=True)
    btn2 = Button("btn2", "Go to Table Menu", x=0, y=0, width=160, height=80, on_press=lambda: print("Already in Table Menu"), selectable=False)
    btn3 = Button("btn3", "Go to Window C", x=0, y=0, width=160, height=80, on_press=lambda: print("Switch to Window C (placeholder)"))
    btn4 = Button("btn4", "Go to Window D", x=0, y=0, width=160, height=80, on_press=lambda: print("Switch to Window D (placeholder)"))
    clock = Clock("main_clock", width=160, height=80,time_format="%H:%M:%S")  # Shows seconds toodate_format="%A, %B %d %Y"  # E.g. "Monday, January 01 2023"
    
    panel1.add_child(btn1)
    panel1.add_child(btn2)
    panel1.add_child(btn3)
    panel1.add_child(btn4)
    panel1.add_child(clock)

    # Panel 2: Table setup (horizontal layout)

    panel2 = Panel("panel2", x=0, y=105, width=820, height=270, layout_type="horizontal")
    programButtonsPanel = Panel("program_buttons_panel", x=0, y=105, width=main_window.width/4, height=270, layout_type="vertical")
    program_names = programs_db.get_all_program_names()
    for program_name in program_names:
        # Create a button for each program
        program_button = Button(
            f"program_btn_{program_name}", 
            program_name, 
            width=main_window.width/4 - 10,
        )
        # Add signals to update the table when a program button is pressed
        def on_pressed(text):
            tableData = programs_db.get_program_data_as_table(text)
            table.set_data(tableData)
            table.set_headers()
            for button in programButtonsPanel.children:
                if isinstance(button, Button) and button.text == text:
                    button.activated = True
                else:
                    button.activated = False
            print(f"Table updated to program: {text}")
        program_button.connect("pressed", on_pressed)
        programButtonsPanel.add_child(program_button)
    
    # Table setup (direct child of main_window)
    # Create table with 3 columns
    table = Table("data_table",x=main_window.width/4,y=105,height=270,width= main_window.width - main_window.width/4, cols=4)
    # Find first program and set its data as the initial table content
    program_names = programs_db.get_all_program_names()
    firstProgram = program_names[0]
    tableData = programs_db.get_program_data_as_table(firstProgram)
    programButtonsPanel.children[0].activated = True  # Activate the first button by default
    # Set complete data (2D list)
    table.set_data(tableData)

    # Or add rows dynamically
    #table.add_row(["Diana", 22, 87])

    # Can also add Element objects directly
    #button = Button("btn1", "Click Me")
    #table.add_row([button, "Some text", "More data"])

    #table.get_cell(0, 1).content = "Updated Header"  # Update cell content directly
    table.set_headers()  # Automatically set first row and column as headers

    panel2.add_child(programButtonsPanel)
    panel2.add_child(table)

    # Panel 3: Exit and placeholder button (horizontal layout)
    panel3 = Panel("panel3", x=0, y=380, width=400, height=100, layout_type="horizontal")
    exit_btn = Button("exit_btn", "Exit", x=0, y=0, width=180, height=80, 
                      on_press=lambda: window_manager.handle_action("exit"))
    placeholder_btn = Button("placeholder_btn", "Placeholder", x=0, y=0, width=180, height=80, 
                            on_press=lambda: print("Placeholder action"))
    panel3.add_child(exit_btn)
    panel3.add_child(placeholder_btn)

    # Assemble main window (panels arranged vertically)
    main_window.add_child(panel1)
    main_window.add_child(panel2)
    main_window.add_child(panel3)

    return main_window, btn1  # Start focus on first button