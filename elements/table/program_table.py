# elements/table/program_table.py
from elements.table.table import Table
from elements.button import Button
from elements.table.cell import Cell
from workout_db.programs_db import ProgramsDB
from elements.base import Element # Needed for isinstance check in Table._sync_children

class ProgramTable(Table):
    def __init__(self, name, program_db, program_name, x=0, y=0, width=200, height=200, selectable=True, draw_box=True):
        # Initialize the Table with 4 columns as expected by ProgramsDB data
        super().__init__(name, x, y, width, height, cols=4, selectable=selectable, draw_box=draw_box)
        self.program_db = program_db
        self.program_name = program_name
        self.add_exercise_button = None
        self.del_exercise_button = None

        # Fetch data from ProgramsDB
        self.table_data = self.program_db.get_program_data_as_table(self.program_name)

        # Set column data types
        self.set_column_type(0, "text")    # Exercise Names
        self.set_column_type(1, "range")   # Rep Range
        self.set_column_type(2, "select")  # Targeted Muscle (assuming 'select' for predefined muscles)
        self.set_column_type(3, "boolean") # Bodyweight?

        self.update_table_data() # Initial population of the table

    def update_table_data(self):
        """
        Fetches data for the current program from ProgramsDB,
        appends action buttons, and updates the table.
        """
        # Fetch latest data from ProgramsDB
        self.table_data = self.program_db.get_program_data_as_table(self.program_name)

        # Create buttons if they don't exist or need recreation
        if self.add_exercise_button is None:
            self.add_exercise_button = Button(
                "add_exercise_btn",
                "Add Exercise",
                on_press=self._on_add_exercise,
                width=self.width // 2 - self.PADDING * 2, # Adjust width based on table width
                height=30
            )
        if self.del_exercise_button is None:
            self.del_exercise_button = Button(
                "del_exercise_btn",
                "Del Exercise",
                on_press=self._on_del_exercise,
                width=self.width // 2 - self.PADDING * 2, # Adjust width based on table width
                height=30
            )

        # Append a new row with buttons to the table data.
        # Ensure the row has 4 columns to match self.cols.
        # The Table's _sync_children method will correctly handle Button objects.
        button_row = [self.add_exercise_button, self.del_exercise_button]
        self.table_data.append(button_row)

        # Set the data, which internally calls _sync_children to create/update cells
        self.set_data(self.table_data)
        # Set headers after data is populated
        self.set_headers()

    def _on_edit_cell(self,row, col, new_value):

        # Edit the cell's text based on the new value

        self.update_table_data() # Refresh table after editing a cell
        
        


    def _on_add_exercise(self):
        """Callback for the 'Add Exercise' button."""
        print(f"Add Exercise button pressed for program: {self.program_name}")
        # Placeholder for adding exercise logic.
        # In a real application, you might open a form to get exercise details.
        dummy_exercise = {
            "name": "New Dummy Exercise",
            "rep_range": "8-12",
            "muscle": "Chest",
            "bodyweight": False
        }
        self.program_db.add_exercise_to_program(self.program_name, dummy_exercise)
        self.update_table_data() # Refresh table after adding

    def _on_del_exercise(self):
        """Callback for the 'Del Exercise' button."""
        print(f"Delete Exercise button pressed for program: {self.program_name}")
        # Placeholder for deleting exercise logic.
        # This currently deletes a dummy exercise or the last one.
        # In a real application, you'd need a way to select which exercise to delete.
        current_exercises = self.program_db.get_program(self.program_name)
        if current_exercises:
            exercise_to_delete = None
            # Try to find and delete a dummy exercise first
            for ex in reversed(current_exercises):
                if ex["name"] == "New Dummy Exercise":
                    exercise_to_delete = ex
                    break
            # If no dummy exercise, delete the last exercise in the list
            if not exercise_to_delete and current_exercises:
                exercise_to_delete = current_exercises[-1]

            if exercise_to_delete:
                self.program_db.remove_exercise_from_program(self.program_name, exercise_to_delete["name"])
                self.update_table_data() # Refresh table after deleting
            else:
                print("No exercises to delete.")
        else:
            print("Program is empty, no exercises to delete.")
