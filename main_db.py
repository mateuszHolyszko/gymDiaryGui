from workout_db_r.Database import Database
from workout_db_r.Exercise import Exercise
from workout_db_r.Program import Program
from workout_db_r.Session import Session
from workout_db_r.Query import Query
if __name__ == "__main__":
    # Initialize database
    db = Database()
    query = Query(db)

    # # Import data from JSON files
    # db.import_from_json(
    #     programs_path="workout_data\programs.json",
    #     sessions_path="workout_data\sessions.json"
    # )

    # # Verify import
    # print(f"Imported {len(db.exercises)} exercises")
    # print(f"Imported {len(db.programs)} programs")

    # # Print verification (compact view)
    # print("\n=== BASIC VERIFICATION ===")
    # db.print_all_programs()
    # db.print_all_sessions(limit=3)  # Show just 3 most recent sessions

    # # Print detailed verification
    # print("\n=== DETAILED VERIFICATION ===")
    # db.print_all_programs(detailed=True)
    # db.print_all_sessions(limit=2, detailed=True)  # Show 2 most recent sessions with 

    # # Print all exercises alphabetically
    # print("\nAll Exercises (Sorted by Name):")
    #db.print_all_exercises(sort_by='name')

    # # Print exercises grouped by target muscle
    # print("\nExercises Grouped by Target:")
    # db.print_all_exercises(group_by_target=True)

    # # Print exercises sorted by target muscle (ungrouped)
    # print("\nExercises Sorted by Target:")
    # db.print_all_exercises(sort_by='target')

    # bench = Exercise("Bench Press", "Chest", False, 2.5)
    # pullup = Exercise("Pull Up", "Back", True, 0.0)
    # db.get_program("Beginner Strength").add_exercise(bench,(2,8))
    # db.get_program("Beginner Strength").add_exercise(pullup,(6,12))

    #print(query.get_exercise_names_by_target("Chest"))
    #print(query.get_last_bodyweight())
    #print(query.get_muscle_workload("Chest")["total_sets"])
    #print(query.get_all_program_names())
    #print(query.get_program_table_data("Push Day"))
    #print(query.get_program_exercises_names("Push Day"))
    #print(query.get_program_exercises_names(query.get_all_program_names()[1]) )
    # print( query.get_session_as_list( "Beginner Strength") )
    # print (query.get_exercise_rep_range("Strength Training","Bench Press"))
    # print( query.get_exercise_by_name("Bench Press").target  )
    #print( query.get_bodyweight_history() )
    #print( query.get_all_targets() )
    #print( query.get_exercise_by_name("Bench Press").get_target_group()  )

        # lastPerformance = sessions.get_last_performance(self.queriedExercise)
        # peakPerformance = sessions.get_peak_performance(self.queriedExercise)
        # totalSets = sessions.get_total_sets_performed(self.queriedExercise)
        # volumeChange = sessions.get_volume_change_percentage(self.queriedExercise)
    
    # print(query.get_last_performance("Bench Press"))
    # print(query.get_peak_performance("Bench Press"))
    # print(query.get_total_sets_performed("Bench Press"))
    # print(query.get_volume_change("Bench Press"))
    
    # Chest exercises
    #db.add_exercise(Exercise("Bench Press", "Chest", False, 2.5))
    # db.add_exercise(Exercise("Incline Bench Press", "Chest", False, 2.5))
    # db.add_exercise(Exercise("Decline Bench Press", "Chest", False, 2.5))
    # db.add_exercise(Exercise("Dumbbell Fly", "Chest", False, 1.25))
    # db.add_exercise(Exercise("Push Up", "Chest", True, 0.0))
    # db.add_exercise(Exercise("Chest Dip", "Chest", True, 0.0))

    # # Back exercises
    # db.add_exercise(Exercise("Deadlift", "Back", False, 5.0))
    # #db.add_exercise(Exercise("Pull Up", "Back", True, 0.0))
    # db.add_exercise(Exercise("Lat Pulldown", "Back", False, 2.5))
    # db.add_exercise(Exercise("Bent Over Row", "Back", False, 2.5))
    # db.add_exercise(Exercise("T-Bar Row", "Back", False, 2.5))
    # db.add_exercise(Exercise("Seated Row", "Back", False, 2.5))

    # # Leg exercises
    # db.add_exercise(Exercise("Squat", "Quads", False, 5.0))
    # db.add_exercise(Exercise("Front Squat", "Quads", False, 2.5))
    # db.add_exercise(Exercise("Leg Press", "Quads", False, 5.0))
    # db.add_exercise(Exercise("Lunge", "Quads", False, 2.5))
    # db.add_exercise(Exercise("Leg Extension", "Quads", False, 1.25))
    # db.add_exercise(Exercise("Romanian Deadlift", "Hamstrings", False, 2.5))
    # db.add_exercise(Exercise("Leg Curl", "Hamstrings", False, 1.25))
    # db.add_exercise(Exercise("Calf Raise", "Calves", False, 2.5))
    # db.add_exercise(Exercise("Hip Thrust", "Glutes", False, 2.5))

    # # Shoulder exercises
    # #db.add_exercise(Exercise("Overhead Press", "Shoulders", False, 2.5))
    # db.add_exercise(Exercise("Arnold Press", "Shoulders", False, 1.25))
    # #db.add_exercise(Exercise("Lateral Raise", "Shoulders", False, 1.25))
    # db.add_exercise(Exercise("Front Raise", "Shoulders", False, 1.25))
    # db.add_exercise(Exercise("Rear Delt Fly", "Shoulders", False, 1.25))

    # # Arm exercises
    # #db.add_exercise(Exercise("Bicep Curl", "Biceps", False, 1.25))
    # db.add_exercise(Exercise("Hammer Curl", "Biceps", False, 1.25))
    # db.add_exercise(Exercise("Preacher Curl", "Biceps", False, 1.25))
    # db.add_exercise(Exercise("Tricep Dip", "Triceps", True, 0.0))
    # db.add_exercise(Exercise("Tricep Pushdown", "Triceps", False, 1.25))
    # db.add_exercise(Exercise("Skull Crusher", "Triceps", False, 1.25))

    # # Core exercises
    # #db.add_exercise(Exercise("Sit Up", "Abs", True, 0.0))
    # db.add_exercise(Exercise("Leg Raise", "Abs", True, 0.0))
    # db.add_exercise(Exercise("Plank", "Abs", True, 0.0))
    # db.add_exercise(Exercise("Russian Twist", "Abs", True, 0.0))

    # # Forearm exercises
    # #db.add_exercise(Exercise("Wrist Curl", "Forearms", False, 1.25))
    # db.add_exercise(Exercise("Reverse Wrist Curl", "Forearms", False, 1.25))
    # db.add_exercise(Exercise("Farmer's Walk", "Forearms", False, 2.5))

    # db.print_all_exercises(sort_by='name')


    print( query.get_last_session_date_by_program("Push Day") )
    print( query.get_program_session_count("Strength Training") )
    print( query.get_program_target_distribution("Strength Training") )