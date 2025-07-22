from typing import List, Dict
from .models import Session
from .database import WorkoutDatabase
from datetime import datetime
from .programs_db import ProgramsDB

class SessionsDB(WorkoutDatabase):
    def get_all_sessions(self) -> List[Dict]:
        """Get all training sessions"""
        return self._read_sessions()

    def add_session(self, session: Dict):
        """Add a new training session"""
        sessions = self._read_sessions()
        sessions.append(session)
        self._write_sessions(sessions)

    def get_sessions_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get sessions between two dates (format: DD-MM-YYYY)"""
        sessions = self._read_sessions()
        return [
            session for session in sessions
            if start_date <= session["date"] <= end_date
        ]

    def get_sessions_by_program(self, program_name: str) -> List[Dict]:
        """Get all sessions for a specific program"""
        sessions = self._read_sessions()
        return [session for session in sessions if session["program"] == program_name]

    def getSessionAsList(self, program_name: str) -> List[list]:
        """
        Returns a table (list of lists) for the last session of the given program.
        Each row: [exercise name, (weight, reps), (weight, reps), ...] for exercises in the program.
        If an exercise from the program is missing in the session, only the name is included in the row.
        """
        programs_db = ProgramsDB()
        sessions = self.get_sessions_by_program(program_name)
        if not sessions:
            program_exercises = programs_db.get_program(program_name)
            exercise_names = [[ex["name"]] for ex in program_exercises]  # Wrap each name in a list
            print(exercise_names)
            return exercise_names
        
        # Find unique sessions by date
        unique_sessions = {}
        for session in sessions:
            date_str = session["date"]
            if date_str not in unique_sessions:
                unique_sessions[date_str] = session
        
        # Get the most recent session
        def parse_date(s):
            return datetime.strptime(s["date"], "%d-%m-%Y")
        
        if not unique_sessions:
            return []
        
        last_session = min(unique_sessions.values(), key=parse_date)
        
        # Debug: Print selected session
        print("Selected session:", last_session)
        
        # Get exercise names from the program
        program_exercises = programs_db.get_program(program_name)
        exercise_names = [ex["name"] for ex in program_exercises]
        
        # Map session exercises by name for quick lookup
        session_ex_dict = {ex["name"]: ex for ex in last_session.get("exercises", [])}
        
        table = []
        for ex_name in exercise_names:
            if ex_name in session_ex_dict:
                row = [ex_name]
                for s in session_ex_dict[ex_name].get("sets", []):
                    row.append((s["weight"], s["reps"]))
                table.append(row)
            else:
                table.append([ex_name])
        
        # Debug: Print final table data
        print("Generated table data:", table)
        return table