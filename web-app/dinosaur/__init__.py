from flask import Blueprint

bp = Blueprint('dinosaur', __name__, url_prefix='/dinosaur')

from . import routes
