import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from app import create_app
from app.extensions import db
from app.models.persona import Persona

app = create_app()

def seed_personas():
    with app.app_context():

        personas = [
            Persona(
                name="Brooder",
                description="You are a dark and broody person, who tends to read dramas, horrors, and dark romance."
            ),
            Persona(
                name="Philosopher",
                description="You probably took a few intro philosophy courses and suddenly think you're in the wrong generation. You tend to read open-ended think pieces and dystopian novels, and you focus on societal themes."
            ),
            Persona(
                name="Stoic",
                description="You find emotions to be a hindrance, or at least say you do to make people think you're cool. To prove this point, you tend to read meditation guides, and a specific type of philosophy works."
            ),
            Persona(
                name="Pretentious",
                description="You read specifically to make people think you're smart, because you're lacking in other traits. Hate to be the one to tell you, but if you need to constantly tell people you're smart, you probably aren't that smart."
            ),
            Persona(
                name="Well-read",
                description="You read a lot of different books, and you've got a pretty diverse set of books you've read. Nice job!"
            ),
            Persona(
                name="Strategist",
                description="You think that you are a hidden tactical genius. You read a lot of books on war, psychology, and autobiographies of famous people. You claim to be preparing for the end times, but if we're being honest, you just like history books and want to make that sound very tough."
            ),
            Persona(
                name="Lovebird",
                description="You're always looking for 'the one,' and you spend a lot of time pining for imaginary people and have some unrealistic expectations. Do I need to say what types of books you read? They're romance ones."
            ),
            Persona(
                name="Scholar",
                description="You spend a lot of time studying and researching. Whether it's for school or you're just like that, that's still pretty good for you."
            ),
            Persona(
                name="Polyglot",
                description="Well look at you, you're cultured and know at least two languages. Very impressive. You read books from the languages you know to try to improve your skills."
            ),
            Persona(
                name="Practical",
                description="You are handy to have around. You mainly read books you can literally apply to your day-to-day life. You mainly read D.I.Y guides, cookbooks, and other useful things."
            ),
            Persona(
                name="Imaginative",
                description="Real life is too boring for you, so you try to stay in your head as an escape from reality. You obviously read fantasy and sci-fi books, but you'll read most types of fiction."
            ),
            Persona(
                name="Not-like-other-readers",
                description="You always mention how quirky, out there, and unique your tastes are. Even if you don't believe some of the things you say, you love being in the spotlight, and being a contrarian is how you do that. You tend to read weird and abstract books."
            )
        ]

        # Prevent duplicates if script is run multiple times
        for persona in personas:
            existing = Persona.query.filter_by(name=persona.name).first()
            if not existing:
                db.session.add(persona)

        db.session.commit()

        print("Personas seeded successfully!")


if __name__ == "__main__":
    seed_personas()