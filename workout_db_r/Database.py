import pickle
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from workout_db_r.Exercise import Exercise
from workout_db_r.Program import Program
from workout_db_r.Session import Session

class Database:
    """Handles storage and retrieval of fitness data using pickle"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)  # Create data directory if it doesn't exist
        
        # Initialize empty databases
        self.exercises: Dict[str, Exercise] = {}
        self.programs: Dict[str, Program] = {}
        self.sessions: Dict[str, List[Session]] = {}  # Key: date, Value: list of sessions
        
        # Load existing data
        self.load_all()
    
    def save_all(self):
        """Save all data to pickle files"""
        self._save_to_file("exercises.pickle", self.exercises)
        self._save_to_file("programs.pickle", self.programs)
        self._save_to_file("sessions.pickle", self.sessions)
    
    def load_all(self):
        """Load all data from pickle files"""
        self.exercises = self._load_from_file("exercises.pickle", {})
        self.programs = self._load_from_file("programs.pickle", {})
        self.sessions = self._load_from_file("sessions.pickle", {})
    
    def _save_to_file(self, filename: str, data):
        """Save data to a pickle file"""
        with open(self.data_dir / filename, 'wb') as f:
            pickle.dump(data, f)
    
    def _load_from_file(self, filename: str, default):
        """Load data from a pickle file, return default if file doesn't exist"""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        return default
    
    # Exercise operations
    def add_exercise(self, exercise: Exercise):
        """Add or update an exercise"""
        self.exercises[exercise.name] = exercise
        self._save_to_file("exercises.pickle", self.exercises)
    
    def get_exercise(self, name: str) -> Exercise:
        """Get an exercise by name"""
        return self.exercises.get(name)
    
    def delete_exercise(self, name: str):
        """Delete an exercise by name"""
        if name in self.exercises:
            del self.exercises[name]
            self._save_to_file("exercises.pickle", self.exercises)
    
    # Program operations
    def add_program(self, program: Program):
        """Add or update a program"""
        self.programs[program.name] = program
        self._save_to_file("programs.pickle", self.programs)
    
    def get_program(self, name: str) -> Program:
        """Get a program by name"""
        return self.programs.get(name)
    
    def delete_program(self, name: str):
        """Delete a program by name"""
        if name in self.programs:
            del self.programs[name]
            self._save_to_file("programs.pickle", self.programs)
    
    # Session operations
    def add_session(self, session: Session):
        """Add a session to the database"""
        if session.date not in self.sessions:
            self.sessions[session.date] = []
        self.sessions[session.date].append(session)
        self._save_to_file("sessions.pickle", self.sessions)
    
    def get_sessions_by_date(self, date: str) -> List[Session]:
        """Get all sessions for a specific date"""
        return self.sessions.get(date, [])
    
    def get_all_sessions(self) -> List[Session]:
        """Get all sessions from the database"""
        return [session for sessions in self.sessions.values() for session in sessions]
    
    def delete_session(self, date: str, index: int):
        """Delete a session by date and index"""
        if date in self.sessions and 0 <= index < len(self.sessions[date]):
            del self.sessions[date][index]
            if not self.sessions[date]:  # Remove date key if no sessions left
                del self.sessions[date]
            self._save_to_file("sessions.pickle", self.sessions)

    # JSON func

    def import_from_json(self, programs_path: str, sessions_path: str):
        """
        Import data from JSON files into the database
        Args:
            programs_path: Path to programs.json
            sessions_path: Path to sessions.json
        """
        # Import programs
        with open(programs_path, 'r') as f:
            programs_data = json.load(f)
            self._import_programs(programs_data['programs'])
        
        # Import sessions
        with open(sessions_path, 'r') as f:
            sessions_data = json.load(f)
            self._import_sessions(sessions_data['sessions'])
    
    def _import_programs(self, programs_data: Dict):
        """Helper to import program data"""
        for program_name, exercises in programs_data.items():
            # Create the program if it doesn't exist
            if program_name not in self.programs:
                self.add_program(Program(program_name))
            
            # Add exercises to program
            program = self.programs[program_name]
            for ex_data in exercises:
                try:
                    # Convert string rep_range to tuple
                    min_rep, max_rep = map(int, ex_data['rep_range'].split('-'))
                    
                    # Handle inconsistent bodyweight format
                    bodyweight = ex_data['bodyweight']
                    if isinstance(bodyweight, str):
                        bodyweight = bodyweight.lower() in ('true', 'yes', '1')
                    
                    # Create exercise
                    exercise = Exercise(
                        name=ex_data['name'],
                        target=ex_data['muscle'],
                        bodyweight=bodyweight,
                        weight_inc=0.0  # Default value since not in JSON
                    )
                    
                    # Add to program
                    program.add_exercise(exercise, (min_rep, max_rep))
                    
                    # Add to exercises database if not exists
                    if exercise.name not in self.exercises:
                        self.add_exercise(exercise)
                        
                except (ValueError, KeyError) as e:
                    print(f"Skipping invalid exercise data: {ex_data}. Error: {e}")
    
    def _import_sessions(self, sessions_data: List[Dict]):
        """Helper to import session data"""
        for session_data in sessions_data:
            try:
                # Get or create the program
                program_name = session_data['program']
                if program_name not in self.programs:
                    self.add_program(Program(program_name))
                program = self.programs[program_name]
                
                # Create session
                session = Session(
                    date=session_data['date'],
                    bodyweight=session_data.get('bodyweight', 0.0),
                    program=program
                )
                
                # Add exercises to session
                for ex_data in session_data['exercises']:
                    # Get or create exercise
                    if ex_data['name'] not in self.exercises:
                        # Create with default values since not all info is in sessions
                        exercise = Exercise(
                            name=ex_data['name'],
                            target="Unknown",  # Default since not in session data
                            bodyweight=False,  # Default
                            weight_inc=0.0     # Default
                        )
                        self.add_exercise(exercise)
                    else:
                        exercise = self.exercises[ex_data['name']]
                    
                    # Add to session
                    session.add_exercise(exercise)
                    
                    # Add sets
                    for set_data in ex_data.get('sets', []):
                        session.add_set_to_exercise(
                            exercise_name=exercise.name,
                            weight=set_data['weight'],
                            reps=set_data['reps']
                        )
                
                # Add session to database
                self.add_session(session)
                
            except (ValueError, KeyError) as e:
                print(f"Skipping invalid session data: {session_data}. Error: {e}")

    # Printing
    def print_all_programs(self, detailed: bool = False):
        """Print all programs with their exercises"""
        print("\n=== PROGRAMS ===")
        for program_name, program in self.programs.items():
            print(f"\nProgram: {program_name}")
            if detailed:
                for exercise, rep_range in program.exercises:
                    print(f"  - {exercise.name}")
                    print(f"    Target: {exercise.target}")
                    print(f"    Bodyweight: {exercise.bodyweight}")
                    print(f"    Weight Increment: {exercise.weight_inc}")
                    print(f"    Rep Range: {rep_range[0]}-{rep_range[1]}")
            else:
                exercises = [ex.name for ex, _ in program.exercises]
                print(f"  Exercises: {', '.join(exercises)}")
        print(f"\nTotal Programs: {len(self.programs)}")

    def print_all_sessions(self, limit: int = 5, detailed: bool = False):
        """Print session summaries with optional detail control"""
        sessions = self.get_all_sessions()
        print("\n=== SESSIONS ===")
        print(f"Total Sessions: {len(sessions)}")
        
        # Sort sessions by date (newest first)
        sessions_sorted = sorted(
            sessions,
            key=lambda s: datetime.strptime(s.date, "%d-%m-%Y"),
            reverse=True
        )
        
        # Print either limited or all sessions based on parameter
        for i, session in enumerate(sessions_sorted[:limit] if limit else sessions_sorted):
            print(f"\nSession {i+1}: {session.date}")
            print(f"  Program: {session.program.name}")
            print(f"  Bodyweight: {session.bodyweight} kg")
            
            if detailed:
                print("  Exercises:")
                for ex_perf in session.exercises:
                    print(f"    - {ex_perf.exercise.name}")
                    for j, set in enumerate(ex_perf.sets, 1):
                        print(f"      Set {j}: {set.weight} kg × {set.reps} reps")
            else:
                ex_counts = len(session.exercises)
                set_counts = sum(len(ex.sets) for ex in session.exercises)
                print(f"  Exercises: {ex_counts}, Total Sets: {set_counts}")
        
        if limit and len(sessions) > limit:
            print(f"\n(Showing {limit} of {len(sessions)} sessions. Set limit=None to see all)")

    def print_all_exercises(self, sort_by: str = 'name', group_by_target: bool = False):
        """
        Print all exercises with their details
        Args:
            sort_by: 'name' or 'target' - how to sort the exercises
            group_by_target: If True, group exercises by their target muscle/group
        """
        exercises = list(self.exercises.values())
        
        # Sort exercises
        if sort_by == 'name':
            exercises.sort(key=lambda x: x.name)
        elif sort_by == 'target':
            exercises.sort(key=lambda x: x.target)
        
        print("\n=== EXERCISES ===")
        print(f"Total Exercises: {len(exercises)}")
        
        if group_by_target:
            # Group by target muscle/group
            targets = {}
            for ex in exercises:
                if ex.target not in targets:
                    targets[ex.target] = []
                targets[ex.target].append(ex)
            
            # Print grouped by target
            for target, ex_list in sorted(targets.items()):
                print(f"\n[{target}]")
                for ex in ex_list:
                    self._print_exercise_details(ex)
        else:
            # Print all exercises in simple list
            for ex in exercises:
                self._print_exercise_details(ex)
    
    def _print_exercise_details(self, exercise: Exercise):
        """Helper method to print details of a single exercise"""
        print(f"\n{exercise.name}")
        print(f"  Target: {exercise.target}")
        print(f"  Bodyweight: {'Yes' if exercise.bodyweight else 'No'}")
        print(f"  Weight Increment: {exercise.weight_inc} kg/lbs")
        
        # Show which programs include this exercise
        programs = []
        for program in self.programs.values():
            if any(ex.name == exercise.name for ex, _ in program.exercises):
                programs.append(program.name)
        
        if programs:
            print(f"  In Programs: {', '.join(programs)}")
        else:
            print("  Not in any program")

# Example usage
if __name__ == "__main__":
    db = Database()
    
    # Create and store sample data
    squat = Exercise("Squat", "legs", False, 2.5)
    db.add_exercise(squat)
    
    program = Program("Beginner Strength")
    program.add_exercise(squat, (5, 8))
    db.add_program(program)
    
    session = Session("24-07-2025", 75.5, program)
    session.add_exercise(squat)
    session.add_set_to_exercise("Squat", 60, 8)
    db.add_session(session)
    
    # Retrieve data
    print("Exercises:", list(db.exercises.keys()))
    print("Programs:", list(db.programs.keys()))
    print("Session dates:", list(db.sessions.keys()))