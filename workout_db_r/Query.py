from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from workout_db_r.Database import Database
from workout_db_r.Exercise import Exercise
from workout_db_r.Program import Program
from workout_db_r.Session import Session
from workout_db_r.Target import Target

class Query:
    """Provides advanced querying capabilities for workout data"""
    
    def __init__(self, database: Database):
        self.db = database
    
    # Exercise-related queries
    def get_all_exercises(self) -> List[Exercise]:
        """Get all exercises in the database"""
        return list(self.db.exercises.values())
    
    def get_exercise_by_name(self, name: str) -> Optional[Exercise]:
        """Get a specific exercise by name"""
        return self.db.exercises.get(name)
    
    def get_exercises_by_target(self, target: str) -> List[dict]:
        """
        Get exercises that target a specific muscle or group
        Args:
            target: Muscle name or group name to filter by
        Returns:
            List of exercise dictionaries with all exercise properties
        """
        return [
            {
                'name': ex.name,
                'target': ex.target,
                'bodyweight': ex.bodyweight,
                'weight_inc': ex.weight_inc,
                'target_color': ex.get_target_color()
            }
            for ex in self.db.exercises.values()
            if target.lower() in [t.lower() for t in ex.get_all_target_muscles()]
        ]
    
    def get_exercise_rep_range(self, program_name: str, exercise_name: str) -> Optional[Tuple[int, int]]:
        """
        Get the rep range for a specific exercise in a specific program
        
        Args:
            program_name: Name of the program to search
            exercise_name: Name of the exercise to find
            
        Returns:
            Tuple of (min_reps, max_reps) if both program and exercise exist,
            None if either program or exercise not found
        """
        program = self.get_program_by_name(program_name)
        if program:
            return program.get_exercise_rep_range(exercise_name)
        return None
    
    def get_exercise_names_by_target(self, target: str) -> List[str]:
        """Get just the names of exercises targeting a specific muscle"""
        if not Target.validate_muscle(target):
            raise ValueError(f"Invalid muscle: {target}. Must be one of: {Target.MUSCLES}")
        
        return [
            ex.name 
            for ex in self.db.exercises.values() 
            if ex.target.lower() == target.lower()
        ]
    
    def get_exercise_names_by_group(self, group: str) -> List[str]:
        """
        Get names of exercises targeting any muscle in a specific group
        
        Args:
            group: Group name to filter by (must be in Target.GROUPS)
        
        Returns:
            List of exercise names that target muscles in the specified group
        
        Raises:
            ValueError: If group is invalid
        """
        if not Target.validate_group(group):
            raise ValueError(f"Invalid group: {group}. Must be one of: {list(Target.GROUPS.keys())}")
        
        muscles_in_group = Target.get_group_muscles(group)
        return [
            ex.name
            for ex in self.db.exercises.values()
            if ex.target in muscles_in_group
        ]
    
    # Program-related queries
    def get_all_programs(self) -> List[Program]:
        """Get all programs in the database"""
        return list(self.db.programs.values())
    
    def get_all_program_names(self) -> List[str]:
        """Get all program names in the database
        
        Returns:
            List of program names as strings
        """
        return list(self.db.programs.keys())
    
    def get_program_by_name(self, name: str) -> Optional[Program]:
        """Get a specific program by name"""
        return self.db.programs.get(name)
    
    def get_all_targets(self) -> List[str]:
        """
        Get all available target muscles in the system
        
        Returns:
            List of all valid target muscle names (from Target.MUSCLES)
        """
        return Target.MUSCLES.copy()  # Return a copy to prevent external modification
    
    def get_program_exercises(self, program_name: str) -> List[Tuple[Exercise, Tuple[int, int]]]:
        """
        Get all exercises in a program with their rep ranges
        Args:
            program_name: Name of the program to query
        Returns:
            List of (Exercise, (min_reps, max_reps)) tuples
        """
        program = self.get_program_by_name(program_name)
        if program:
            return program.exercises
        return []
    
    def get_program_exercises_names(self, program_name: str) -> List[str]:
        """
        Get all exercise names in a program
        Args:
            program_name: Name of the program to query
        Returns:
            List of exercise names as strings
        """
        program = self.get_program_by_name(program_name)
        if program:
            return [exercise.name for exercise, _ in program.exercises]
        return []

    
    def get_program_table_data(self, program_name: str) -> List[List]:
        """
        Get program data in table format
        Returns:
            [
                ["Exercise Name", "Rep Range", "Target", "Bodyweight"],
                ["Squat", "5-8", "legs", False],
                ...
            ]
        """
        program = self.get_program_by_name(program_name)
        if not program:
            return []
        
        table = [["Exercise Name", "Rep Range", "Target", "Bodyweight"]]
        for exercise, rep_range in program.exercises:
            table.append([
                exercise.name,
                f"{rep_range[0]}-{rep_range[1]}",
                exercise.target,
                exercise.bodyweight
            ])
        return table
    
    # Session-related queries
    def get_all_sessions(self) -> List[Session]:
        """Get all sessions from the database"""
        return self.db.get_all_sessions()
    
    def get_sessions_by_date(self, date: str) -> List[Session]:
        """Get sessions on a specific date (DD-MM-YYYY format)"""
        return self.db.get_sessions_by_date(date)
    
    def get_sessions_by_date_range(self, start_date: str, end_date: str) -> List[Session]:
        """
        Get sessions between two dates (inclusive)
        Args:
            start_date: DD-MM-YYYY format
            end_date: DD-MM-YYYY format
        """
        all_sessions = self.get_all_sessions()
        return [
            s for s in all_sessions
            if start_date <= s.date <= end_date
        ]
    
    def get_sessions_by_program(self, program_name: str) -> List[Session]:
        """Get all sessions for a specific program"""
        return [
            s for s in self.get_all_sessions()
            if s.program.name == program_name
        ]
    
    def get_last_session(self) -> Optional[Session]:
        """Get the most recent session by date"""
        sessions = self.get_all_sessions()
        if not sessions:
            return None
        return max(sessions, key=lambda s: datetime.strptime(s.date, "%d-%m-%Y"))
    
    def get_last_bodyweight(self) -> Optional[float]:
        """Get the most recent bodyweight measurement"""
        last_session = self.get_last_session()
        return last_session.bodyweight if last_session else None
    
    # Performance tracking queries
    def get_exercise_history(self, exercise_name: str, weeks: int = None) -> Tuple[List[Dict], List[str]]:
        """
        Get historical performance data for an exercise
        Args:
            exercise_name: Name of exercise to track
            weeks: Optional number of weeks to look back
        Returns:
            Tuple of (performance_data, dates) where:
                performance_data: List of dicts with keys:
                    - weight: float
                    - reps: int
                    - volume: float (weight * reps)
                dates: List of date strings (DD-MM-YYYY)
        """
        sessions = self.get_all_sessions()
        if weeks:
            cutoff_date = datetime.now() - timedelta(weeks=weeks)
            sessions = [s for s in sessions if datetime.strptime(s.date, "%d-%m-%Y") >= cutoff_date]
        
        performance_data = []
        dates = []
        
        for session in sessions:
            for ex_perf in session.exercises:
                if ex_perf.exercise.name == exercise_name and ex_perf.sets:
                    best_set = ex_perf.best_set()
                    if best_set:
                        performance_data.append({
                            'weight': best_set.weight,
                            'reps': best_set.reps,
                            'volume': best_set.weight * best_set.reps
                        })
                        dates.append(session.date)
        
        # Sort by date (newest first)
        combined = sorted(zip(dates, performance_data),
                        key=lambda x: datetime.strptime(x[0], "%d-%m-%Y"),
                        reverse=True)
        if combined:
            dates, performance_data = zip(*combined)
            return list(performance_data), list(dates)
        return [], []
    
    def get_last_performance(self, exercise_name: str) -> Optional[dict]:
        """
        Return the most recent performance for a given exercise.
        
        Args:
            exercise_name: Name of exercise to search for
            
        Returns:
            dict with keys: 'sets', 'weight', 'reps', 'date' or None if not found
        """
        sessions = sorted(
            self.get_all_sessions(),
            key=lambda s: datetime.strptime(s.date, "%d-%m-%Y"),
            reverse=True
        )

        for session in sessions:
            for ex_perf in session.exercises:
                if ex_perf.exercise.name == exercise_name and ex_perf.sets:
                    first_set = ex_perf.sets[0]
                    return {
                        "sets": len(ex_perf.sets),
                        "weight": first_set.weight,
                        "reps": first_set.reps,
                        "date": session.date
                    }
        return None
    
    def get_bodyweight_history(self, weeks: int = None) -> Tuple[List[float], List[str]]:
        """
        Get historical bodyweight data with corresponding dates.
        
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
        
        # Get current date for comparison if weeks parameter is provided
        current_date = datetime.now() if weeks else None
        
        for session in sessions:
            # Skip sessions without bodyweight data
            if session.bodyweight is None:
                continue
                
            try:
                session_date = datetime.strptime(session.date, "%d-%m-%Y")
                
                # Filter by weeks if specified
                if weeks and (current_date - session_date) > timedelta(weeks=weeks):
                    continue
                    
                dates.append(session.date)
                bodyweights.append(session.bodyweight)
                
            except ValueError:
                # Skip if date format is invalid
                continue
        
        # Sort by date (newest first)
        combined = sorted(zip(dates, bodyweights),
                        key=lambda x: datetime.strptime(x[0], "%d-%m-%Y"),
                        reverse=True)
        
        if combined:
            dates, bodyweights = zip(*combined)
            return list(bodyweights), list(dates)
        return [], []
    
    def get_peak_performance(self, exercise_name: str) -> Optional[Dict]:
        """
        Get the peak performance for an exercise
        Returns:
            Dict with keys: weight, reps, volume, date
            or None if no data found
        """
        history, dates = self.get_exercise_history(exercise_name)
        if not history:
            return None
        
        peak = max(history, key=lambda x: x['volume'])
        peak_date = dates[history.index(peak)]
        return {
            'weight': peak['weight'],
            'reps': peak['reps'],
            'volume': peak['volume'],
            'date': peak_date
        }
    
    def get_total_sets_performed(self, exercise_name: str, weeks: int = 4) -> int:
        """
        Return the total number of sets performed for a given exercise in the specified time period.
        
        Args:
            exercise_name: Name of exercise to count sets for
            weeks: Time period to look back in weeks (default=4)
            
        Returns:
            int: Total number of sets performed
        """
        total_sets = 0
        cutoff_date = datetime.now() - timedelta(weeks=weeks)

        for session in self.get_all_sessions():
            try:
                session_date = datetime.strptime(session.date, "%d-%m-%Y")
                if session_date < cutoff_date:
                    continue
                    
                for ex_perf in session.exercises:
                    if ex_perf.exercise.name == exercise_name and ex_perf.sets:
                        total_sets += len(ex_perf.sets)
            except ValueError:
                continue

        return total_sets
    
    def get_volume_change(self, exercise_name: str, weeks: int = 4) -> Optional[float]:
        """
        Calculate volume change percentage over time period
        Args:
            exercise_name: Exercise to analyze
            weeks: Time period in weeks (default: 4)
        Returns:
            Percentage change (positive or negative) or None if not enough data
        """
        history, dates = self.get_exercise_history(exercise_name, weeks)
        if len(history) < 2:
            return None
        
        first_volume = history[-1]['volume']  # Oldest session
        last_volume = history[0]['volume']    # Newest session
        
        if first_volume == 0:
            return None
        
        return round( ((last_volume - first_volume) / first_volume) * 100 , 1 )
    
    def get_muscle_workload(self, muscle: str, weeks: int = None) -> Dict:
        """
        Get workload statistics for a specific muscle
        Args:
            muscle: Muscle name to analyze (must be in Target.MUSCLES)
            weeks: Optional time period in weeks
        Returns:
            Dict with keys:
                - total_sets: int
                - total_volume: float
                - exercises: List of exercise names
        """
        # Validate muscle exists
        if not Target.validate_muscle(muscle):
            raise ValueError(f"Invalid muscle: {muscle}. Must be one of: {Target.MUSCLES}")
        
        sessions = self.get_all_sessions()
        if weeks:
            cutoff_date = datetime.now() - timedelta(weeks=weeks)
            sessions = [s for s in sessions if datetime.strptime(s.date, "%d-%m-%Y") >= cutoff_date]
        
        exercises = set()
        total_sets = 0
        total_volume = 0.0
        
        for session in sessions:
            for ex_perf in session.exercises:
                # Direct comparison since exercises now only target muscles
                if ex_perf.exercise.target.lower() == muscle.lower():
                    exercises.add(ex_perf.exercise.name)
                    total_sets += len(ex_perf.sets)
                    total_volume += sum(s.weight * s.reps for s in ex_perf.sets)
        
        return {
            'total_sets': total_sets,
            'total_volume': total_volume,
            'exercises': list(exercises)
        }
    
    def get_program_completion(self, program_name: str) -> Dict[str, float]:
        """
        Calculate completion percentages for exercises in a program
        Args:
            program_name: Program to analyze
        Returns:
            Dict with exercise names as keys and completion percentages as values
        """
        program = self.get_program_by_name(program_name)
        if not program:
            return {}
        
        last_session = next(
            (s for s in reversed(self.get_sessions_by_program(program_name))),
            None
        )
        
        if not last_session:
            return {ex.name: 0.0 for ex, _ in program.exercises}
        
        completion = {}
        session_exercises = {ex.exercise.name for ex in last_session.exercises}
        
        for exercise, _ in program.exercises:
            completion[exercise.name] = 100.0 if exercise.name in session_exercises else 0.0
        
        return completion
    
    def get_session_as_list(self, program_name: str) -> List[list]:
        """
        Returns a table (list of lists) for the last session of the given program.
        Each row: [exercise name, (weight, reps), (weight, reps), ...] for exercises in the program.
        If an exercise from the program is missing in the session, only the name is included in the row.
        
        Args:
            program_name: Name of the program to query
            
        Returns:
            List of lists representing the session table
        """
        # Get the program
        program = self.get_program_by_name(program_name)
        if not program:
            return []
        
        # Get sessions for this program
        sessions = self.get_sessions_by_program(program_name)
        if not sessions:
            # Return just exercise names if no sessions exist
            return [[ex.name] for ex, _ in program.exercises]
        
        # Find the most recent session
        def parse_date(session):
            return datetime.strptime(session.date, "%d-%m-%Y")
        
        last_session = max(sessions, key=parse_date)
        
        # Create mapping of exercise names to their performance in session
        session_exercises = {
            ex_perf.exercise.name: ex_perf 
            for ex_perf in last_session.exercises
        }
        
        # Build the result table
        table = []
        for exercise, _ in program.exercises:
            ex_name = exercise.name
            if ex_name in session_exercises:
                # Exercise was performed - add all sets
                row = [ex_name]
                for set in session_exercises[ex_name].sets:
                    row.append((set.weight, set.reps))
                table.append(row)
            else:
                # Exercise not performed - just add name
                table.append([ex_name])
        
        return table
    
    def add_session(self, session_data: dict) -> bool:
        """
        Add a new session from JSON data to the database and save to file
        
        Args:
            session_data: Dictionary containing session data in format:
                {
                    'date': 'DD-MM-YYYY',
                    'program': 'Program Name',
                    'bodyweight': float,
                    'exercises': [
                        {
                            'name': 'Exercise Name',
                            'sets': [
                                {'weight': float, 'reps': int},
                                ...
                            ]
                        },
                        ...
                    ]
                }
                
        Returns:
            bool: True if session was added successfully, False otherwise
        """
        try:
            # Validate required fields
            required_fields = ['date', 'program', 'exercises']
            if not all(field in session_data for field in required_fields):
                raise ValueError("Missing required session fields")
            
            # Get or create the program
            program_name = session_data['program']
            program = self.db.get_program(program_name)
            if not program:
                # Create a minimal program if it doesn't exist
                program = Program(program_name)
                self.db.add_program(program)
            
            # Create the session
            session = Session(
                date=session_data['date'],
                bodyweight=session_data.get('bodyweight', 0.0),
                program=program
            )
            
            # Add exercises and sets
            for ex_data in session_data['exercises']:
                # Get or create exercise
                exercise = self.db.get_exercise(ex_data['name'])
                if not exercise:
                    # Create with default values if exercise doesn't exist
                    exercise = Exercise(
                        name=ex_data['name'],
                        target="Unknown",  # Default target
                        bodyweight=False,  # Default
                        weight_inc=0.0     # Default
                    )
                    self.db.add_exercise(exercise)
                
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
            self.db.add_session(session)
            
            # Save to file
            self.db.save_all()
            return True
            
        except Exception as e:
            print(f"Error adding session: {str(e)}")
            return False