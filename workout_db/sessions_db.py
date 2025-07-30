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
        
        last_session = max(unique_sessions.values(), key=parse_date)
        
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
    
    def get_last_session(self) -> Dict:
        """Get the most recent session (by date)
        Returns None if no sessions exist for the program.
        """
        sessions = self.get_all_sessions()
        if not sessions:
            return None

        # Parse dates and find the session with the latest date
        def parse_date(session):
            return datetime.strptime(session["date"], "%d-%m-%Y")

        return max(sessions, key=parse_date)
    
    def get_last_bodyweight(self) -> float:
        """Get the most recent bodyweight recorded across all sessions.
        Returns None if no sessions exist or no bodyweight is recorded.
        """
        try:
            # Get the most recent session
            last_session = self.get_last_session()
            if last_session is None:
                return None
                
            # Safely get bodyweight from session (returns None if key doesn't exist)
            return last_session.get('bodyweight')
            
        except Exception as e:
            print(f"Error retrieving last bodyweight: {str(e)}")
            return None
        
    def get_sets_for_target_whole(self, targetMuscle: str) -> int:
        """Get the total number of sets for exercises targeting a specific muscle group.
        
        Args:
            targetMuscle: The muscle group to count sets for (e.g., "Chest", "Back")
            
        Returns:
            int: Total number of sets across all programs' most recent sessions
        """
        programs_db = ProgramsDB()
        total_sets = 0
        
        # Get all programs - returns dict like {"Strength Training": [...exercises], ...}
        all_programs = programs_db.get_all_programs()
        
        # Iterate through each program
        for program_name, exercises_data in all_programs.items():
            # Get the most recent session for this program
            sessions = self.get_sessions_by_program(program_name)
            if not sessions:
                continue
                
            # Find the most recent session
            def parse_date(session):
                return datetime.strptime(session["date"], "%d-%m-%Y")
            latest_session = max(sessions, key=parse_date)
            
            # Convert to Session dataclass for easier handling
            session_obj = Session.from_dict(latest_session)
            
            # Create set of exercise names that target our muscle
            target_exercises = {
                ex["name"] for ex in exercises_data 
                if ex.get("muscle") == targetMuscle
            }
            
            # Count sets for target exercises in this session
            for exercise in session_obj.exercises:
                if exercise.name in target_exercises:
                    total_sets += len(exercise.sets)
        
        return total_sets
    
    def get_bodyweight_history(self, weeks: int = None) -> tuple[List[float], List[str]]:
        """Get historical bodyweight data with corresponding dates.
        
        Args:
            weeks: Optional number of weeks to look back. If None, returns all data.
            
        Returns:
            tuple: (bodyweights, dates) where:
                - bodyweights: List of float bodyweight values (most recent first)
                - dates: List of corresponding date strings in "DD-MM-YYYY" format
        """
        sessions = self.get_all_sessions()
        bodyweights = []
        dates = []
        
        # Get current date for comparison
        current_date = datetime.now()
        
        for session in sessions:
            if 'bodyweight' in session and session['bodyweight'] is not None:
                try:
                    session_date = datetime.strptime(session['date'], "%d-%m-%Y")
                    
                    # If weeks parameter is provided, check if session is within range
                    if weeks is not None:
                        time_delta = current_date - session_date
                        if time_delta.days > weeks * 7:  # Convert weeks to days
                            continue
                    
                    bodyweights.append(session['bodyweight'])
                    dates.append(session['date'])
                except ValueError:
                    # Skip if date format is invalid
                    continue
        
        # Sort by date (most recent first)
        combined = sorted(zip(dates, bodyweights), 
                        key=lambda x: datetime.strptime(x[0], "%d-%m-%Y"), 
                        reverse=True)
        if combined:
            dates, bodyweights = zip(*combined)
            return list(bodyweights), list(dates)
        return [], []
    
    def get_exercise_history(self, exercise_name: str, weeks: int = None) -> tuple[List[dict], List[str]]:
        """Get historical exercise performance data with corresponding dates.
        
        Args:
            exercise_name: Name of exercise to track
            weeks: Optional number of weeks to look back. If None, returns all data.
            
        Returns:
            tuple: (performance_data, dates) where:
                - performance_data: List of dicts with:
                    - "weight": float
                    - "reps": int  
                    - "volume": weight*reps
                - dates: List of corresponding session dates ("DD-MM-YYYY")
        """
        sessions = self.get_all_sessions()
        performance_data = []
        dates = []
        
        current_date = datetime.now()
        
        for session in sessions:
            try:
                session_date = datetime.strptime(session['date'], "%d-%m-%Y")
                
                # Check if session is within time range
                if weeks is not None:
                    time_delta = current_date - session_date
                    if time_delta.days > weeks * 7:
                        continue
                
                # Find the exercise in session
                for exercise in session.get('exercises', []):
                    if exercise['name'] == exercise_name:
                        # Calculate best set (by volume)
                        best_set = max(
                            exercise.get('sets', []),
                            key=lambda s: s['weight'] * s['reps'],
                            default=None
                        )
                        
                        if best_set:
                            volume = best_set['weight'] * best_set['reps']
                            performance_data.append({
                                "weight": best_set['weight'],
                                "reps": best_set['reps'],
                                "volume": volume
                            })
                            dates.append(session['date'])
                        break
                        
            except (ValueError, KeyError):
                continue
        
        # Sort by date (newest first)
        combined = sorted(zip(dates, performance_data),
                        key=lambda x: datetime.strptime(x[0], "%d-%m-%Y"),
                        reverse=True)
        
        if combined:
            dates, performance_data = zip(*combined)
            return list(performance_data), list(dates)
        return [], []