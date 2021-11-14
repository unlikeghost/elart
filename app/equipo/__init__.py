from flask import Blueprint

equipo_bp = Blueprint('equipo', __name__)

from . import routes
