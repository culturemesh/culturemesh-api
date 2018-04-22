from flask import Blueprint
from api import require_apikey

users = Blueprint('user', __name__)

@users.route("/ping")
@require_apikey
def test():
    return "pong"
