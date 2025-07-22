"""
exercises.py - Static exercise database with muscle group targeting
"""

class Exercises:
    # List of all possible muscle targets
    TARGETS = ["Chest", "Back", "Quads", "Hamstrings", "Shoulders", 
               "Biceps", "Triceps", "Abs", "Calves", "Glutes", "Forearms"]
    
    # Exercise database (exercise_name: primary_target)
    EXERCISE_DB = {
        # Chest exercises
        "Bench Press": "Chest",
        "Incline Bench Press": "Chest",
        "Decline Bench Press": "Chest",
        "Dumbbell Fly": "Chest",
        "Push Up": "Chest",
        "Chest Dip": "Chest",
        
        # Back exercises
        "Deadlift": "Back",
        "Pull Up": "Back",
        "Lat Pulldown": "Back",
        "Bent Over Row": "Back",
        "T-Bar Row": "Back",
        "Seated Row": "Back",
        
        # Leg exercises
        "Squat": "Quads",
        "Front Squat": "Quads",
        "Leg Press": "Quads",
        "Lunge": "Quads",
        "Leg Extension": "Quads",
        "Romanian Deadlift": "Hamstrings",
        "Leg Curl": "Hamstrings",
        "Calf Raise": "Calves",
        "Hip Thrust": "Glutes",
        
        # Shoulder exercises
        "Overhead Press": "Shoulders",
        "Arnold Press": "Shoulders",
        "Lateral Raise": "Shoulders",
        "Front Raise": "Shoulders",
        "Rear Delt Fly": "Shoulders",
        
        # Arm exercises
        "Bicep Curl": "Biceps",
        "Hammer Curl": "Biceps",
        "Preacher Curl": "Biceps",
        "Tricep Dip": "Triceps",
        "Tricep Pushdown": "Triceps",
        "Skull Crusher": "Triceps",
        
        # Core exercises
        "Sit Up": "Abs",
        "Leg Raise": "Abs",
        "Plank": "Abs",
        "Russian Twist": "Abs",
        
        # Forearm exercises
        "Wrist Curl": "Forearms",
        "Reverse Wrist Curl": "Forearms",
        "Farmer's Walk": "Forearms"
    }
    
    @staticmethod
    def get_target_muscle(exercise_name: str) -> str:
        """Get the primary target muscle for an exercise"""
        return Exercises.EXERCISE_DB.get(exercise_name, "Unknown")
    
    @staticmethod
    def get_exercises_for_muscle(target_muscle: str) -> list:
        """Get all exercises that target a specific muscle group"""
        if target_muscle not in Exercises.TARGETS:
            return []
        return [ex for ex, muscle in Exercises.EXERCISE_DB.items() if muscle == target_muscle]
    
    @staticmethod
    def get_all_exercises() -> list:
        """Get all exercises in the database"""
        return list(Exercises.EXERCISE_DB.keys())
    
    @staticmethod
    def exercise_exists(exercise_name: str) -> bool:
        """Check if an exercise exists in the database"""
        return exercise_name in Exercises.EXERCISE_DB