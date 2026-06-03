# COMP305FinalProject
This is the repository for the final project

How to run the app (development server):
- Create a virtual environment and install dependencies
- In the terminal with environment activated:
    - set FLASK_APP=app
    - set FLASK_ENV=development

Use to make sure database schema is up-to-date (in the terminal):  
- flask db upgrade

To populate the Books table:  
- python scripts/load_books.py

To populate the Users table:  
- python scripts/seed_users.py

To populate the persona table:  
- python scripts/fill_personas.py

To run the app (in the terminal): 
- flask run