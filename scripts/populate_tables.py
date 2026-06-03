#this script is used to populate the database with initial data for testing and development purposes. It runs other scripts that add books, users, and personas.
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


from app import create_app
from app.extensions import db

from scripts.load_books import load_books
from scripts.seed_users import seed_users
from scripts.fill_personas import seed_personas

def main():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        load_books()
        seed_users()
        seed_personas()