import dearpygui.dearpygui as dpg
from workout_db_r.Program import Program
from workout_db_r.Target import Target
from .db_setup import db

# --- Callbacks ---
def delete_program_cb(sender, app_data, user_data):
    db.delete_program(user_data)
    refresh_program_list()
    refresh_edit_program_section()

def move_exercise_up_cb(sender, app_data, user_data):
    """Move an exercise up in the program's exercise list"""
    prog_name, ex_name = user_data
    program = db.get_program(prog_name)
    exercises = program.exercises
    
    # Find the index of the exercise to move
    index = next((i for i, (ex, _) in enumerate(exercises) if ex.name == ex_name), None)
    
    if index is not None and index > 0:
        # Swap with the exercise above it
        exercises[index], exercises[index-1] = exercises[index-1], exercises[index]
        db.add_program(program)
        refresh_edit_program_section()

def move_exercise_down_cb(sender, app_data, user_data):
    """Move an exercise down in the program's exercise list"""
    prog_name, ex_name = user_data
    program = db.get_program(prog_name)
    exercises = program.exercises
    
    # Find the index of the exercise to move
    index = next((i for i, (ex, _) in enumerate(exercises) if ex.name == ex_name), None)
    
    if index is not None and index < len(exercises) - 1:
        # Swap with the exercise below it
        exercises[index], exercises[index+1] = exercises[index+1], exercises[index]
        db.add_program(program)
        refresh_edit_program_section()

def refresh_program_list():
    if dpg.does_item_exist("program_list"):
        dpg.delete_item("program_list", children_only=True)
    for prog in db.programs.values():
        with dpg.group(parent="program_list", horizontal=True):
            dpg.add_text(prog.name)
            dpg.add_button(label="Delete", callback=delete_program_cb, user_data=prog.name)
    dpg.configure_item("edit_prog_select", items=list(db.programs.keys()))

def refresh_edit_program_section():
    if not dpg.does_item_exist("edit_prog_ex_list"):
        return
    dpg.delete_item("edit_prog_ex_list", children_only=True)
    prog_name = dpg.get_value("edit_prog_select")
    if not prog_name or prog_name not in db.programs:
        return
    
    program = db.get_program(prog_name)
    for i, (ex, reps) in enumerate(program.exercises):
        with dpg.group(parent="edit_prog_ex_list", horizontal=True):
            # Add up/down arrows only if there's more than one exercise
            if len(program.exercises) > 1:
                # Up arrow (disabled for first item)
                dpg.add_button(
                    label="Up",
                    width=35,
                    enabled=(i > 0),
                    callback=move_exercise_up_cb,
                    user_data=(prog_name, ex.name)
                )
                # Down arrow (disabled for last item)
                dpg.add_button(
                    label="Down",
                    width=35,
                    enabled=(i < len(program.exercises) - 1),
                    callback=move_exercise_down_cb,
                    user_data=(prog_name, ex.name)
                )
            
            dpg.add_text(f"{ex.name} ({reps[0]}-{reps[1]} reps)")
            dpg.add_button(
                label="Remove",
                callback=remove_ex_from_prog_cb,
                user_data=(prog_name, ex.name)
            )

def remove_ex_from_prog_cb(sender, app_data, user_data):
    prog_name, ex_name = user_data
    program = db.get_program(prog_name)
    program.remove_exercise(ex_name)
    db.add_program(program)
    refresh_edit_program_section()

def apply_exercise_filters():
    """Filter the exercises dropdown based on current filters"""
    name_filter = dpg.get_value("prog_ex_filter_name").lower()
    target_filter = dpg.get_value("prog_ex_filter_target")
    
    filtered_exercises = [
        name for name, ex in db.exercises.items()
        if (name_filter in name.lower()) and 
           (target_filter == "All" or ex.target == target_filter)
    ]
    
    dpg.configure_item("edit_prog_ex_select", items=filtered_exercises)

def clear_exercise_filters():
    """Clear all exercise filters"""
    dpg.set_value("prog_ex_filter_name", "")
    dpg.set_value("prog_ex_filter_target", "All")
    apply_exercise_filters()

def add_ex_to_prog_cb():
    prog_name = dpg.get_value("edit_prog_select")
    ex_name = dpg.get_value("edit_prog_ex_select")
    min_rep = dpg.get_value("edit_prog_min_rep")
    max_rep = dpg.get_value("edit_prog_max_rep")
    if prog_name not in db.programs or ex_name not in db.exercises:
        return
    try:
        program = db.get_program(prog_name)
        program.add_exercise(db.get_exercise(ex_name), (int(min_rep), int(max_rep)))
        db.add_program(program)
        refresh_edit_program_section()
    except Exception as e:
        print("Error adding exercise to program:", e)

def add_program_cb():
    name = dpg.get_value("add_prog_name")
    if not name.strip():
        return
    if name not in db.programs:
        db.add_program(Program(name))
    refresh_program_list()

def build_programs_tab():
    with dpg.tab(label="Programs"):
        # Program List
        dpg.add_text("Program List")
        with dpg.child_window(tag="program_list", height=150, autosize_x=True):
            pass
        
        # Edit Program Section
        dpg.add_separator()
        dpg.add_text("Edit Program")
        dpg.add_combo(
            tag="edit_prog_select", 
            label="Select Program", 
            items=list(db.programs.keys()),
            callback=lambda s, a, u: refresh_edit_program_section()
        )
        with dpg.child_window(tag="edit_prog_ex_list", height=100, autosize_x=True):
            pass
        
        # Add Exercise to Program with Filters
        dpg.add_separator()
        dpg.add_text("Add Exercise to Program")
        
        # Exercise Filters
        with dpg.group(horizontal=True):
            dpg.add_text("Filter Exercises:")
            dpg.add_input_text(
                label="Name", 
                tag="prog_ex_filter_name", 
                width=150,
                callback=lambda s, a, u: apply_exercise_filters()
            )
            dpg.add_combo(
                label="Target", 
                tag="prog_ex_filter_target", 
                items=["All"] + Target.MUSCLES, 
                default_value="All",
                width=150,
                callback=lambda s, a, u: apply_exercise_filters()
            )
            dpg.add_button(
                label="Clear", 
                callback=clear_exercise_filters
            )
        
        # Exercise selection and rep inputs
        dpg.add_combo(
            tag="edit_prog_ex_select", 
            label="Exercise", 
            items=list(db.exercises.keys())
        )
        dpg.add_input_int(label="Min Rep", tag="edit_prog_min_rep", default_value=5)
        dpg.add_input_int(label="Max Rep", tag="edit_prog_max_rep", default_value=10)
        dpg.add_button(label="Add to Program", callback=add_ex_to_prog_cb)
        
        # Add New Program
        dpg.add_separator()
        dpg.add_text("Add New Program")
        dpg.add_input_text(label="Name", tag="add_prog_name")
        dpg.add_button(label="Add Program", callback=add_program_cb)
    
    # Initialize filters
    apply_exercise_filters()
    refresh_program_list()