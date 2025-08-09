class Target:
    """Static class containing muscle and group definitions with colors"""
    MUSCLES = ["Chest", "Back", "Quads", "Hamstrings", "Shoulders", 
               "Biceps", "Triceps", "Abs", "Calves", "Glutes", "Forearms"]
    
    GROUPS = {
        "torso_front": ["Chest", "Shoulders", "Abs"],
        "torso_back": ["Back", "Shoulders"],
        "legs": ["Quads", "Hamstrings", "Calves", "Glutes"],
        "arms": ["Biceps", "Triceps", "Forearms"]
    }
    
    COLOR_PALETTE = [
        (255, 102, 102),  # Chest
        (255, 178, 102),  # Back
        (153, 255, 51),   # Quads
        (51, 255, 51),    # Hamstrings
        (51, 255, 153),   # Glutes
        (102, 102, 255),  # Shoulders
        (102, 255, 255),  # Biceps
        (102, 178, 255),  # Triceps
        (178, 102, 255),  # Abs
        (255, 102, 255),  # Calves
        (255, 102, 178)   # Forearms
    ]
    
    MUSCLE_TO_COLOR = dict(zip(MUSCLES, COLOR_PALETTE))
    
    @classmethod
    def get_muscle_color(cls, muscle):
        """Get RGB color for a muscle"""
        return cls.MUSCLE_TO_COLOR.get(muscle, (200, 200, 200))  # Default gray
    
    @classmethod
    def get_group_muscles(cls, group):
        """Get muscles belonging to a group"""
        return cls.GROUPS.get(group, [])
    
    @classmethod
    def validate_muscle(cls, muscle):
        """Check if muscle exists in the system"""
        return muscle in cls.MUSCLES
    
    @classmethod
    def validate_group(cls, group):
        """Check if group exists in the system"""
        return group in cls.GROUPS
    
    @classmethod
    def get_muscle_group(cls, muscle: str) -> str:
        """Get the primary group for a muscle"""
        for group, muscles in cls.GROUPS.items():
            if muscle in muscles:
                return group
        raise ValueError(f"Muscle {muscle} not found in any group")
