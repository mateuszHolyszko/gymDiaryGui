from dataclasses import dataclass, field
from typing import List, Dict, Optional
import datetime

@dataclass
class Exercise:
    name: str
    rep_range: str
    muscle: str
    bodyweight: bool

@dataclass
class Program:
    name: str
    exercises: List[Exercise] = field(default_factory=list)

@dataclass
class Set:
    weight: float
    reps: int

@dataclass
class SessionExercise:
    name: str
    sets: List[Set] = field(default_factory=list)

@dataclass
class Session:
    date: str  # Format: DD-MM-YYYY
    program: str
    exercises: List[SessionExercise] = field(default_factory=list)

    def to_dict(self):
        return {
            "date": self.date,
            "program": self.program,
            "exercises": [{
                "name": ex.name,
                "sets": [{"weight": s.weight, "reps": s.reps} for s in ex.sets]
            } for ex in self.exercises]
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            date=data["date"],
            program=data["program"],
            exercises=[
                SessionExercise(
                    name=ex["name"],
                    sets=[Set(weight=s["weight"], reps=s["reps"]) for s in ex["sets"]]
                ) for ex in data["exercises"]
            ]
        )