from workout_db.programs_db import ProgramsDB
from workout_db.sessions_db import SessionsDB

# Initialize the databases
programs_db = ProgramsDB()
sessions_db = SessionsDB()

# Add a new program
programs_db.add_program("Strength Training")

# Add exercises to a program
exercise = {
    "name": "Bench Press",
    "rep_range": "8-12",
    "muscle": "Chest",
    "bodyweight": False
}
programs_db.add_exercise_to_program("Strength Training", exercise)

# Get all programs
all_programs = programs_db.get_all_programs()
#print(all_programs)

# Add a new session
new_session = {
    "date": "04-08-2024",
    "program": "Strength Training",
    "exercises": [
        {
            "name": "Bench Press",
            "sets": [
                {"weight": 100, "reps": 10},
                {"weight": 95, "reps": 8}
            ]
        },
        {
            "name": "Push Ups",
            "sets": []
        }
    ]
}
sessions_db.add_session(new_session)

# Get all sessions
all_sessions = sessions_db.get_all_sessions()
#print(all_sessions)

# Get program data in table format
table_data = programs_db.get_program_data_as_table("Strength Training")

# Print the table
for row in table_data:
    print(row)