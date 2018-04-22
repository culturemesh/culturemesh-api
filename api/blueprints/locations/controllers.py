from flask import Blueprint
from api import require_apikey

locations = Blueprint('location', __name__)

@locations.route("/ping")
@require_apikey
def test():
    return "pong"
