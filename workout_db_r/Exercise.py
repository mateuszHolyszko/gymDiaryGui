from workout_db_r.Target import Target
class Exercise:
    def __init__(self, name: str, target: str, bodyweight: bool, weight_inc: float):
        """
        Exercise object for custom database
        
        Parameters:
        - name (str): Name of the exercise
        - target (str): Target muscle (must exist in Target.MUSCLES)
        - bodyweight (bool): Whether the exercise is bodyweight-only
        - weight_inc (float): Weight increment for progression (0.0 for bodyweight)
        """
        if not Target.validate_muscle(target):
            raise ValueError(f"Invalid target muscle: {target}. Must be one of: {Target.MUSCLES}")
        self.name = name
        self.target = target  # Now guaranteed to be a single muscle
        self.bodyweight = bodyweight
        self.weight_inc = weight_inc
    
    def __repr__(self):
        return f"Exercise(name='{self.name}', target='{self.target}', bodyweight={self.bodyweight}, weight_inc={self.weight_inc})"
    
    def to_dict(self):
        """Convert Exercise object to dictionary for easy storage"""
        return {
            'name': self.name,
            'target': self.target,
            'bodyweight': self.bodyweight,
            'weight_inc': self.weight_inc
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Exercise object from dictionary"""
        return cls(
            name=data['name'],
            target=data['target'],
            bodyweight=data['bodyweight'],
            weight_inc=data['weight_inc']
        )
    
    def get_target_color(self):
        """Get color for the target muscle"""
        return Target.get_muscle_color(self.target)

    
    def get_target_group(self) -> str:
        """Get the primary group this muscle belongs to"""
        for group, muscles in Target.GROUPS.items():
            if self.target in muscles:
                return group
        return "unknown"