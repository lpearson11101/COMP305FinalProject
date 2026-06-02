import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from app import create_app
from app.extensions import db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

def seed_users():
    with app.app_context():

        # Optional: clear existing users (comment out if not needed)
        # db.session.query(User).delete()

        users = [
            User(
                username="admin",
                password_hash=generate_password_hash("admin123"),
                role="admin"
            ),
            User(
                username="Cliff_Spab",
                password_hash=generate_password_hash("password123"),
                role="user"
            ),
            User(
                username="Jack_Gladney",
                password_hash=generate_password_hash("password123"),
                role="user"
            ),
        ]

        # Avoid duplicates if re-running script
        for u in users:
            existing = User.query.filter_by(username=u.username).first()
            if not existing:
                db.session.add(u)

        db.session.commit()

        print("Seeded users successfully!")


if __name__ == "__main__":
    seed_users()