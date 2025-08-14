from pathlib import Path
from workout_db_r.Database import Database

DATA_DIR = Path(__file__).parent / ".." / "workout_db_r" / "data"

class CustomDB(Database):
    def __init__(self):
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(exist_ok=True)
        self.exercises = {}
        self.programs = {}
        self.sessions = {}
        self.load_all()

db = CustomDB()
