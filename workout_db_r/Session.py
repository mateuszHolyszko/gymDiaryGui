from datetime import datetime
from typing import List, Dict, Optional
from workout_db_r.Exercise import Exercise
from workout_db_r.Program import Program

class Set:
    """Class representing a single set of an exercise"""
    def __init__(self, weight: float, reps: int):
        self.weight = weight
        self.reps = reps
    
    def __repr__(self):
        return f"Set(weight={self.weight}, reps={self.reps})"
    
    def to_dict(self):
        return {'weight': self.weight, 'reps': self.reps}
    
    @classmethod
    def from_dict(cls, data):
        return cls(data['weight'], data['reps'])


class ExercisePerformance:
    """Class representing performance of one exercise in a session"""
    def __init__(self, exercise: Exercise):
        self.exercise = exercise
        self.sets: List[Set] = []
    
    def add_set(self, weight: float, reps: int):
        """Add a completed set to this exercise"""
        self.sets.append(Set(weight, reps))
    
    def best_set(self) -> Optional[Set]:
        """Return the best set by weight x reps volume"""
        if not self.sets:
            return None
        return max(self.sets, key=lambda s: s.weight * s.reps)
    
    def __repr__(self):
        sets_str = "\n".join(f"  {i+1}. {set}" for i, set in enumerate(self.sets))
        return f"ExercisePerformance({self.exercise.name}):\n{sets_str}"
    
    def to_dict(self):
        return {
            'exercise': self.exercise.to_dict(),
            'sets': [set.to_dict() for set in self.sets]
        }
    
    @classmethod
    def from_dict(cls, data):
        perf = cls(Exercise.from_dict(data['exercise']))
        perf.sets = [Set.from_dict(set_data) for set_data in data['sets']]
        return perf


class Session:
    """Class representing a workout session"""
    def __init__(self, date: str, bodyweight: float, program: Program):
        """
        Create a workout session
        
        Parameters:
        - date (str): Date in DD-MM-YYYY format
        - bodyweight (float): User's bodyweight in kg/lbs
        - program (Program): Reference to the program used
        """
        self.date = self._validate_date(date)
        self.bodyweight = bodyweight
        self.program = program
        self.exercises: List[ExercisePerformance] = []
    
    def _validate_date(self, date_str: str) -> str:
        """Validate and standardize date format"""
        try:
            date_obj = datetime.strptime(date_str, "%d-%m-%Y")
            return date_obj.strftime("%d-%m-%Y")  # Standardize format
        except ValueError:
            raise ValueError("Date must be in DD-MM-YYYY format")
    
    def add_exercise(self, exercise: Exercise):
        """Add an exercise to track in this session"""
        if not any(ex[0].name == exercise.name for ex in self.program.exercises):
            raise ValueError("Exercise not in program")
        self.exercises.append(ExercisePerformance(exercise))
    
    def add_set_to_exercise(self, exercise_name: str, weight: float, reps: int):
        """Add a completed set to an exercise in this session"""
        for ex_perf in self.exercises:
            if ex_perf.exercise.name.lower() == exercise_name.lower():
                ex_perf.add_set(weight, reps)
                return
        raise ValueError(f"Exercise '{exercise_name}' not found in session")
    
    def total_volume(self) -> float:
        """Calculate total volume (weight x reps) for all exercises"""
        return sum(
            set.weight * set.reps
            for ex_perf in self.exercises
            for set in ex_perf.sets
        )
    
    def __repr__(self):
        exercises_str = "\n".join(str(ex) for ex in self.exercises)
        return (
            f"Session on {self.date}\n"
            f"Bodyweight: {self.bodyweight}\n"
            f"Program: {self.program.name}\n"
            f"Exercises:\n{exercises_str}"
        )
    
    def to_dict(self):
        return {
            'date': self.date,
            'bodyweight': self.bodyweight,
            'program': self.program.to_dict(),
            'exercises': [ex.to_dict() for ex in self.exercises]
        }
    
    @classmethod
    def from_dict(cls, data):
        session = cls(
            data['date'],
            data['bodyweight'],
            Program.from_dict(data['program'])
        )
        session.exercises = [
            ExercisePerformance.from_dict(ex_data)
            for ex_data in data['exercises']
        ]
        return session


# Example Usage
if __name__ == "__main__":
    # Create program and exercises
    program = Program("Beginner Strength")
    squat = Exercise("Squat", "legs", False, 2.5)
    pushup = Exercise("Push-up", "Chest", True, 0.0)
    program.add_exercise(squat, (5, 8))
    program.add_exercise(pushup, (8, 12))
    
    # Create session
    session = Session("24-07-2025", 75.5, program)
    
    # Add exercises to session
    session.add_exercise(squat)
    session.add_exercise(pushup)
    
    # Log workout sets
    session.add_set_to_exercise("Squat", 60, 8)
    session.add_set_to_exercise("Squat", 65, 6)
    session.add_set_to_exercise("Squat", 70, 5)
    session.add_set_to_exercise("Push-up", session.bodyweight * 0.6, 10)
    session.add_set_to_exercise("Push-up", session.bodyweight * 0.6, 9)
    
    # Display session
    print(session)
    print(f"\nTotal Volume: {session.total_volume():.1f}")
    
    # Best sets
    for ex in session.exercises:
        best = ex.best_set()
        print(f"\nBest set for {ex.exercise.name}: {best}")