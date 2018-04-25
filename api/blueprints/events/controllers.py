from flask import Blueprint
from api import require_apikey

events = Blueprint('event', __name__)

@events.route("/ping")
@require_apikey
def test():
    return "pong"
