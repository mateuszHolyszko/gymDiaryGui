import json
import os
from typing import Dict, List
from pathlib import Path
from .models import Program, Exercise, Session

class WorkoutDatabase:
    def __init__(self, db_dir: str = "workout_data"):
        self.db_dir = Path(db_dir)
        self.programs_file = self.db_dir / "programs.json"
        self.sessions_file = self.db_dir / "sessions.json"
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database directory and files if they don't exist"""
        self.db_dir.mkdir(exist_ok=True)
        
        if not self.programs_file.exists():
            with open(self.programs_file, 'w') as f:
                json.dump({"programs": {}}, f)
                
        if not self.sessions_file.exists():
            with open(self.sessions_file, 'w') as f:
                json.dump({"sessions": []}, f)

    def _read_programs(self) -> Dict[str, List[Dict]]:
        with open(self.programs_file, 'r') as f:
            return json.load(f)["programs"]

    def _write_programs(self, programs: Dict[str, List[Dict]]):
        with open(self.programs_file, 'w') as f:
            json.dump({"programs": programs}, f, indent=2)

    def _read_sessions(self) -> List[Dict]:
        with open(self.sessions_file, 'r') as f:
            return json.load(f)["sessions"]

    def _write_sessions(self, sessions: List[Dict]):
        with open(self.sessions_file, 'w') as f:
            json.dump({"sessions": sessions}, f, indent=2)