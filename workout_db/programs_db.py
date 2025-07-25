from typing import Dict, List
from .models import Program, Exercise
from .database import WorkoutDatabase

class ProgramsDB(WorkoutDatabase):
    def get_all_programs(self) -> Dict[str, List[Dict]]:
        """Get all programs with their exercises"""
        return self._read_programs()
    
    def get_all_program_names(self) -> list:
        """Returns a list of all program names in the database"""
        programs = self._read_programs()  # This gets the full programs dictionary
        return list(programs.keys())  # Convert the dictionary keys to a list

    def get_program(self, program_name: str) -> List[Dict]:
        """Get a specific program by name"""
        programs = self._read_programs()
        return programs.get(program_name, [])

    def add_program(self, program_name: str):
        """Add a new empty program"""
        programs = self._read_programs()
        if program_name not in programs:
            programs[program_name] = []
            self._write_programs(programs)

    def delete_program(self, program_name: str):
        """Delete a program"""
        programs = self._read_programs()
        if program_name in programs:
            del programs[program_name]
            self._write_programs(programs)

    def add_exercise_to_program(self, program_name: str, exercise: Dict):
        """Add an exercise to a program"""
        programs = self._read_programs()
        if program_name in programs:
            programs[program_name].append(exercise)
            self._write_programs(programs)

    def remove_exercise_from_program(self, program_name: str, exercise_name: str):
        """Remove an exercise from a program"""
        programs = self._read_programs()
        if program_name in programs:
            programs[program_name] = [
                ex for ex in programs[program_name] 
                if ex["name"] != exercise_name
            ]
            self._write_programs(programs)

    def get_program_data_as_table(self, program_name: str) -> list:
        """
        Returns program data in table format:
        [
            ["Exercise Names", "Rep Range", "Targeted Muscle", "Bodyweight?"],
            [ex1, rep_range1, muscle1, True/False],
            ...
        ]
        """
        programs = self._read_programs()
        program_exercises = programs.get(program_name, [])
        
        if not program_exercises:
            return []
        
        # Create the table with header row
        table_data = [
            ["Exercise Names", "Rep Range", "Targeted Muscle", "Bodyweight?"]
        ]
        
        # Add each exercise as a row
        for exercise in program_exercises:
            row = [
                exercise["name"],
                exercise["rep_range"],
                exercise["muscle"],
                exercise["bodyweight"]
            ]
            table_data.append(row)
        
        return table_data