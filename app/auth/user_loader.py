from app.extensions import login_manager
from app.models.user import User

# This function is used by Flask-Login to load a user from the database given their user ID. 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))