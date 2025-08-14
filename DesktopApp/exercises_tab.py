import dearpygui.dearpygui as dpg
from workout_db_r.Exercise import Exercise
from workout_db_r.Target import Target
from .db_setup import db

# --- Callbacks ---
def delete_exercise_cb(sender, app_data, user_data):
    db.delete_exercise(user_data)
    refresh_exercise_list()

def add_exercise_cb():
    try:
        ex = Exercise(
            name=dpg.get_value("ex_name"),
            target=dpg.get_value("ex_target"),
            bodyweight=dpg.get_value("ex_bodyweight"),
            weight_inc=float(dpg.get_value("ex_weight_inc") or 0)
        )
        db.add_exercise(ex)
        refresh_exercise_list()
    except Exception as e:
        print("Error adding exercise:", e)

def edit_exercise_cb(sender, app_data, user_data):
    """Open edit popup for selected exercise."""
    exercise_name = user_data
    exercise = db.exercises[exercise_name]
    
    # Store current exercise name for reference
    dpg.set_value("edit_original_name", exercise_name)
    dpg.set_value("edit_ex_name", exercise.name)
    dpg.set_value("edit_ex_target", exercise.target)
    dpg.set_value("edit_ex_bodyweight", exercise.bodyweight)
    dpg.set_value("edit_ex_weight_inc", str(exercise.weight_inc))
    
    dpg.show_item("edit_exercise_popup")

def save_edited_exercise_cb():
    """Save changes to the edited exercise."""
    try:
        original_name = dpg.get_value("edit_original_name")
        new_name = dpg.get_value("edit_ex_name")
        
        # Create updated exercise
        updated_ex = Exercise(
            name=new_name,
            target=dpg.get_value("edit_ex_target"),  # Updated to use new tag
            bodyweight=dpg.get_value("edit_ex_bodyweight"),
            weight_inc=float(dpg.get_value("edit_ex_weight_inc") or 0)
        )
        
        # Handle name change if needed
        if original_name != new_name:
            db.delete_exercise(original_name)
        
        db.add_exercise(updated_ex)
        refresh_exercise_list()
        dpg.hide_item("edit_exercise_popup")
    except Exception as e:
        print("Error saving exercise:", e)

def apply_filters_cb():
    """Apply the current filters to the exercise list."""
    refresh_exercise_list()

def clear_filters_cb():
    """Clear all filters and show all exercises."""
    dpg.set_value("filter_name", "")
    dpg.set_value("filter_target", "All")
    refresh_exercise_list()

def refresh_exercise_list():
    """Refresh the exercise list based on current filters."""
    if dpg.does_item_exist("exercise_list"):
        dpg.delete_item("exercise_list", children_only=True)
    
    # Get filter values
    name_filter = dpg.get_value("filter_name").lower()
    target_filter = dpg.get_value("filter_target")
    
    # Filter exercises
    filtered_exercises = [
        ex for ex in db.exercises.values()
        if (name_filter in ex.name.lower()) and 
           (target_filter == "All" or ex.target == target_filter)
    ]
    
    # Sort by name
    filtered_exercises.sort(key=lambda x: x.name)
    
    # Display filtered exercises
    for ex in filtered_exercises:
        with dpg.group(parent="exercise_list", horizontal=True):
            dpg.add_text(f"{ex.name} ({ex.target})")
            dpg.add_text("BW" if ex.bodyweight else f"{ex.weight_inc}kg")
            dpg.add_button(
                label="Edit",
                callback=edit_exercise_cb,
                user_data=ex.name
            )
            dpg.add_button(
                label="Delete",
                callback=delete_exercise_cb,
                user_data=ex.name
            )

def build_exercises_tab():
    with dpg.tab(label="Exercises"):
        # Filter Section
        with dpg.group(horizontal=True):
            dpg.add_text("Filter by:")
            dpg.add_input_text(label="Name", tag="filter_name", width=150, 
                             callback=lambda s, a, u: apply_filters_cb())
            dpg.add_combo(label="Target", tag="filter_target", 
                         items=["All"] + Target.MUSCLES, default_value="All",
                         width=150, callback=lambda s, a, u: apply_filters_cb())
            dpg.add_button(label="Clear Filters", callback=clear_filters_cb)
        
        # Exercise List
        dpg.add_text("Exercise List")
        with dpg.child_window(tag="exercise_list", height=200, autosize_x=True):
            pass
        
        # Add Exercise Form
        dpg.add_separator()
        dpg.add_text("Add New Exercise")
        dpg.add_input_text(label="Name", tag="ex_name")
        dpg.add_combo(label="Target", tag="ex_target", items=Target.MUSCLES, default_value=Target.MUSCLES[0])
        dpg.add_checkbox(label="Bodyweight", tag="ex_bodyweight")
        dpg.add_input_text(label="Weight Increment (kg)", tag="ex_weight_inc")
        dpg.add_button(label="Add Exercise", callback=add_exercise_cb)
        
        # Edit Exercise Popup (hidden by default)
        with dpg.window(
            label="Edit Exercise",
            tag="edit_exercise_popup",
            modal=True,
            show=False,
            width=400,
            height=300
        ):
            dpg.add_input_text(label="Original Name", tag="edit_original_name", readonly=True)
            dpg.add_input_text(label="Name", tag="edit_ex_name")
            dpg.add_combo(label="Target", tag="edit_ex_target", items=Target.MUSCLES)
            dpg.add_checkbox(label="Bodyweight", tag="edit_ex_bodyweight")
            dpg.add_input_text(label="Weight Increment (kg)", tag="edit_ex_weight_inc")
            dpg.add_button(label="Save Changes", callback=save_edited_exercise_cb)
            dpg.add_button(label="Cancel", callback=lambda: dpg.hide_item("edit_exercise_popup"))
    
    refresh_exercise_list()