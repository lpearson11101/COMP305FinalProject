from flask import Blueprint

bp = Blueprint('models', __name__)
from app.models.user import User