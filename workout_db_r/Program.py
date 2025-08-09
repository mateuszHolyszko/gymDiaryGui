from typing import Dict, List, Tuple, Optional
from workout_db_r.Exercise import Exercise
from workout_db_r.Target import Target
class Program:
    def __init__(self, name: str):
        """
        A workout program containing exercises with rep ranges
        
        Parameters:
        - name (str): Name of the program
        """
        self.name = name
        self.exercises: List[Tuple[Exercise, Tuple[int, int]]] = []  # (Exercise, (min_reps, max_reps))
    
    def add_exercise(self, exercise: Exercise, rep_range: Tuple[int, int]):
        """
        Add an exercise to the program with its rep range
        
        Parameters:
        - exercise (Exercise): Exercise object to add
        - rep_range (tuple): (min_reps, max_reps) for this exercise in the program
        """
        if not isinstance(exercise, Exercise):
            raise TypeError("Must provide an Exercise object")
        if len(rep_range) != 2 or not all(isinstance(x, int) for x in rep_range):
            raise ValueError("Rep range must be a tuple of two integers")
        if rep_range[0] > rep_range[1]:
            raise ValueError("Min reps cannot be greater than max reps")
            
        self.exercises.append((exercise, rep_range))
    
    def remove_exercise(self, exercise_name: str):
        """
        Remove an exercise from the program by name
        
        Parameters:
        - exercise_name (str): Name of exercise to remove
        """
        self.exercises = [
            (ex, reps) for (ex, reps) in self.exercises 
            if ex.name.lower() != exercise_name.lower()
        ]
    
    def get_exercises_by_target(self, target: str) -> List[Tuple[Exercise, Tuple[int, int]]]:
        """
        Get all exercises targeting a specific muscle/group
        
        Parameters:
        - target (str): Muscle or group name to filter by
        
        Returns:
        - List of (Exercise, rep_range) tuples that match the target
        """
        return [
            (ex, reps) for (ex, reps) in self.exercises
            if target.lower() in [t.lower() for t in ex.get_all_target_muscles()]
        ]
    
    def get_exercise_rep_range(self, exercise_name: str) -> Optional[Tuple[int, int]]:
        """
        Get the rep range for a specific exercise in this program
        
        Args:
            exercise_name: Name of the exercise to find
            
        Returns:
            Tuple of (min_reps, max_reps) if exercise exists in program,
            None if exercise not found
        """
        for exercise, rep_range in self.exercises:
            if exercise.name.lower() == exercise_name.lower():
                return rep_range
        return None
    
    def to_dict(self) -> Dict:
        """
        Convert Program to dictionary for storage
        
        Returns:
        - Dictionary representation of the program
        """
        return {
            'name': self.name,
            'exercises': [
                {
                    'exercise': ex.to_dict(),
                    'rep_range': rep_range
                }
                for ex, rep_range in self.exercises
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Program':
        """
        Create Program from dictionary
        
        Parameters:
        - data (dict): Dictionary representation of program
        
        Returns:
        - Program object
        """
        program = cls(data['name'])
        for item in data['exercises']:
            exercise = Exercise.from_dict(item['exercise'])
            program.add_exercise(exercise, tuple(item['rep_range']))
        return program
    
    def __repr__(self) -> str:
        exercise_list = "\n".join(
            f"- {ex.name} ({ex.target}): {reps[0]}-{reps[1]} reps"
            for ex, reps in self.exercises
        )
        return f"Program: {self.name}\nExercises:\n{exercise_list}"


# Example Usage:
if __name__ == "__main__":
    # Create some exercises
    squat = Exercise("Barbell Squat", "legs", False, 5.0)
    bench = Exercise("Bench Press", "Chest", False, 2.5)
    pullup = Exercise("Pull Up", "Back", True, 0.0)
    
    # Create a program
    strength_program = Program("5x5 Strength")
    
    # Add exercises with rep ranges
    strength_program.add_exercise(squat, (5, 5))
    strength_program.add_exercise(bench, (5, 5))
    strength_program.add_exercise(pullup, (5, 8))
    
    # Display program
    print(strength_program)
    
    # Convert to dict and back
    program_dict = strength_program.to_dict()
    reconstructed = Program.from_dict(program_dict)
    
    # Get exercises by target
    print("\nLeg exercises:")
    for ex, reps in reconstructed.get_exercises_by_target("Quads"):
        print(f"{ex.name}: {reps[0]}-{reps[1]} reps")