import json
from datetime import datetime
from typing import Dict, List

def validate_program_data(program_data: Dict) -> bool:
    """Validate program data structure"""
    required_keys = {"name", "rep_range", "muscle", "bodyweight"}
    return all(key in program_data for key in required_keys)

def validate_session_data(session_data: Dict) -> bool:
    """Validate session data structure"""
    if not all(key in session_data for key in ["date", "program", "exercises"]):
        return False
    
    try:
        datetime.strptime(session_data["date"], "%d-%m-%Y")
    except ValueError:
        return False
    
    for exercise in session_data["exercises"]:
        if "name" not in exercise or "sets" not in exercise:
            return False
        for set_ in exercise["sets"]:
            if "weight" not in set_ or "reps" not in set_:
                return False
                
    return True

def format_exercise(exercise: Dict) -> str:
    """Format exercise data for display"""
    return (
        f"{exercise['name']} "
        f"(Muscle: {exercise['muscle']}, "
        f"Reps: {exercise['rep_range']}, "
        f"Bodyweight: {'Yes' if exercise['bodyweight'] else 'No'})"
    )