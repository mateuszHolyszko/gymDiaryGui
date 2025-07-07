from typing import List, Dict
from .models import Session
from .database import WorkoutDatabase

class SessionsDB(WorkoutDatabase):
    def get_all_sessions(self) -> List[Dict]:
        """Get all training sessions"""
        return self._read_sessions()

    def add_session(self, session: Dict):
        """Add a new training session"""
        sessions = self._read_sessions()
        sessions.append(session)
        self._write_sessions(sessions)

    def get_sessions_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get sessions between two dates (format: DD-MM-YYYY)"""
        sessions = self._read_sessions()
        return [
            session for session in sessions
            if start_date <= session["date"] <= end_date
        ]

    def get_sessions_by_program(self, program_name: str) -> List[Dict]:
        """Get all sessions for a specific program"""
        sessions = self._read_sessions()
        return [session for session in sessions if session["program"] == program_name]